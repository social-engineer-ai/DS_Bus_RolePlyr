"""LLM-based grader for short-answer quiz questions.

Grades each answer on an attempt using a quiz-level grading instruction plus a
per-question rubric and model answer, then writes the LLM-assigned points and
reasoning back to the QuizAnswer record. Keeps needs_review=true so the
instructor can confirm or override every LLM grade.
"""

from __future__ import annotations

import asyncio
import json
import logging
import re
from typing import Optional

from sqlalchemy.orm import Session

from app.models.quiz import Quiz, QuizAttempt, QuizAnswer, QuizQuestion
from app.services.llm_client import get_llm_client

logger = logging.getLogger(__name__)


DEFAULT_GRADER_MODEL = "claude-opus-4-7"

SYSTEM_PROMPT = (
    "You are an experienced teaching assistant grading short-answer quiz responses. "
    "Apply the rubric thoughtfully. Reward understanding expressed in plain language; "
    "when a student uses technical terms, look for evidence they understand what the terms mean. "
    "Respond only with valid JSON matching the requested schema."
)


def _build_user_prompt(
    quiz: Quiz,
    question: QuizQuestion,
    student_answer: str,
) -> str:
    rubric_text = ""
    if question.rubric:
        try:
            rubric_text = json.dumps(question.rubric, indent=2)
        except (TypeError, ValueError):
            rubric_text = str(question.rubric)

    parts = [
        "# Grading task",
        "",
        "Grade the student's answer to the question below using the rubric. "
        f"Points available: {question.points}. Partial credit is allowed "
        "(any value between 0 and the maximum, inclusive).",
        "",
        "## Quiz-wide grading guidance",
        (quiz.grading_instructions or "").strip() or "(none provided)",
    ]

    if quiz.hw_reference:
        parts += ["", "## Context about the homework this quiz references", quiz.hw_reference.strip()]

    parts += [
        "",
        "## Question",
        question.question_text.strip(),
        "",
        "## Rubric (tiers and criteria)",
        rubric_text or "(no structured rubric provided)",
    ]

    if question.model_answer:
        parts += ["", "## Model answer (for reference)", question.model_answer.strip()]

    if question.common_wrong_answers:
        parts += [
            "",
            "## Common wrong answers to watch for",
            question.common_wrong_answers.strip(),
        ]

    parts += [
        "",
        "## Student's answer",
        student_answer.strip() or "(blank)",
        "",
        "## Output",
        "Return JSON with this exact shape:",
        "{",
        '  "points_awarded": <number between 0 and ' + str(question.points) + ">,",
        '  "tier": "<rubric tier label, e.g. full / partial / minimal / none>",',
        '  "reasoning": "<2-4 sentences explaining the score, citing the rubric>"',
        "}",
        "Do not include any text outside the JSON object.",
    ]

    return "\n".join(parts)


def _extract_json(text: str) -> dict:
    """Pull the first JSON object out of a model response."""
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not match:
        raise ValueError(f"No JSON object found in grader response: {text[:200]}")
    return json.loads(match.group(0))


async def _grade_single_answer(
    quiz: Quiz,
    question: QuizQuestion,
    answer: QuizAnswer,
    model: str,
) -> tuple[float, Optional[str], Optional[bool]]:
    """Grade one answer. Returns (points_awarded, reasoning, is_correct)."""
    if not answer.student_answer or not answer.student_answer.strip():
        return 0.0, "Blank answer — no credit.", False

    llm = get_llm_client()
    user_prompt = _build_user_prompt(quiz, question, answer.student_answer)

    raw = await llm.generate_json_response(
        system_prompt=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
        max_tokens=800,
        model=model,
    )

    try:
        data = _extract_json(raw)
    except (ValueError, json.JSONDecodeError) as e:
        logger.exception("Grader returned unparseable JSON for answer %s", answer.id)
        return 0.0, f"Grader error (unparseable response): {e}. Please grade manually.", None

    try:
        points = float(data.get("points_awarded", 0))
    except (TypeError, ValueError):
        points = 0.0
    points = max(0.0, min(points, float(question.points)))

    reasoning = str(data.get("reasoning", "")).strip() or None
    tier = str(data.get("tier", "")).strip().lower()
    if tier:
        reasoning = f"[{tier}] {reasoning}" if reasoning else f"[{tier}]"

    # "is_correct" is a loose notion for partial credit. Mark True only at full credit.
    is_correct = points >= float(question.points) - 1e-6

    return points, reasoning, is_correct


async def grade_attempt_with_llm(
    db: Session,
    attempt_id,
    *,
    model: Optional[str] = None,
    regrade: bool = False,
) -> dict:
    """Grade every eligible answer on an attempt using the LLM.

    Args:
        db: DB session.
        attempt_id: QuizAttempt UUID.
        model: Override the quiz's configured model.
        regrade: If False, skip answers that already have graded_by != "none".
                 If True, re-grade everything.

    Returns:
        Summary dict: {"graded": int, "skipped": int, "failed": int, "total_score": float}.
    """
    attempt = db.query(QuizAttempt).filter(QuizAttempt.id == attempt_id).first()
    if not attempt:
        raise ValueError(f"Attempt {attempt_id} not found")

    quiz = db.query(Quiz).filter(Quiz.id == attempt.quiz_id).first()
    if not quiz:
        raise ValueError(f"Quiz {attempt.quiz_id} not found")

    grader_model = model or quiz.llm_grader_model or DEFAULT_GRADER_MODEL

    questions = db.query(QuizQuestion).filter(QuizQuestion.quiz_id == quiz.id).all()
    question_map = {q.id: q for q in questions}

    answers = db.query(QuizAnswer).filter(QuizAnswer.attempt_id == attempt.id).all()

    to_grade: list[QuizAnswer] = []
    skipped = 0
    for a in answers:
        question = question_map.get(a.question_id)
        if not question:
            skipped += 1
            continue
        # Only LLM-grade short-answer / self-authored style questions
        if question.question_type not in ("short_answer", "self_authored"):
            skipped += 1
            continue
        if not regrade and a.graded_by and a.graded_by != "none":
            skipped += 1
            continue
        to_grade.append(a)

    # Grade in parallel (up to 5 concurrent calls — reasonable for Anthropic rate limits)
    sem = asyncio.Semaphore(5)

    async def _run(a: QuizAnswer):
        async with sem:
            q = question_map[a.question_id]
            try:
                return a, await _grade_single_answer(quiz, q, a, grader_model)
            except Exception as e:  # noqa: BLE001
                logger.exception("Grader failed for answer %s", a.id)
                return a, (0.0, f"Grader error: {e}. Please grade manually.", None)

    results = await asyncio.gather(*[_run(a) for a in to_grade])

    graded = 0
    failed = 0
    for a, (points, reasoning, is_correct) in results:
        a.points_awarded = points
        a.grader_reasoning = reasoning
        a.is_correct = is_correct
        a.graded_by = "llm"
        # Keep needs_review=true so the instructor confirms every LLM grade.
        a.needs_review = True
        if reasoning and reasoning.lower().startswith("grader error"):
            failed += 1
        else:
            graded += 1

    # Recompute attempt score across all answers
    all_answers = db.query(QuizAnswer).filter(QuizAnswer.attempt_id == attempt.id).all()
    attempt.score = sum(x.points_awarded for x in all_answers)

    db.commit()

    return {
        "graded": graded,
        "skipped": skipped,
        "failed": failed,
        "total_score": attempt.score,
    }
