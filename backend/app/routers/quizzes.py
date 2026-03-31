"""Quiz API endpoints."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.quiz import Quiz, QuizQuestion, QuizAttempt, QuizAnswer
from app.models.user import User
from app.schemas.quiz import (
    QuizCreate,
    QuizUpdate,
    QuizDetailResponse,
    QuizListItem,
    QuestionResponse,
    StudentQuiz,
    StudentQuestionView,
    AttemptSubmit,
    AttemptResponse,
    AnswerResult,
    AttemptListItem,
    AnswerGrade,
)
from app.routers.auth import get_current_user

router = APIRouter()


def _require_instructor(current_user: User):
    if current_user.role.value not in ["instructor", "admin"]:
        raise HTTPException(status_code=403, detail="Instructor access required")


# ---- Instructor endpoints ----

@router.post("", response_model=QuizDetailResponse)
async def create_quiz(
    quiz_data: QuizCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new quiz with questions (instructor only)."""
    _require_instructor(current_user)

    quiz = Quiz(
        course_id=quiz_data.course_id,
        title=quiz_data.title,
        description=quiz_data.description,
        time_limit_minutes=quiz_data.time_limit_minutes,
        max_attempts=quiz_data.max_attempts,
        due_date=quiz_data.due_date,
        is_active=quiz_data.is_active,
        show_answers_after_submit=quiz_data.show_answers_after_submit,
    )
    db.add(quiz)
    db.flush()

    questions = []
    for i, q_data in enumerate(quiz_data.questions):
        question = QuizQuestion(
            quiz_id=quiz.id,
            question_type=q_data.question_type,
            question_text=q_data.question_text,
            options=q_data.options,
            correct_answer=q_data.correct_answer,
            acceptable_answers=q_data.acceptable_answers,
            points=q_data.points,
            order_index=q_data.order_index if q_data.order_index else i,
        )
        questions.append(question)
    db.add_all(questions)
    db.commit()
    db.refresh(quiz)

    total_points = sum(q.points for q in questions)

    return QuizDetailResponse(
        id=quiz.id,
        course_id=quiz.course_id,
        title=quiz.title,
        description=quiz.description,
        time_limit_minutes=quiz.time_limit_minutes,
        max_attempts=quiz.max_attempts,
        due_date=quiz.due_date,
        is_active=quiz.is_active,
        show_answers_after_submit=quiz.show_answers_after_submit,
        question_count=len(questions),
        total_points=total_points,
        created_at=quiz.created_at,
        questions=[
            QuestionResponse(
                id=q.id,
                question_type=q.question_type,
                question_text=q.question_text,
                options=q.options,
                correct_answer=q.correct_answer,
                acceptable_answers=q.acceptable_answers,
                points=q.points,
                order_index=q.order_index,
            )
            for q in questions
        ],
    )


@router.get("", response_model=List[QuizListItem])
async def list_quizzes(
    course_id: Optional[UUID] = None,
    active_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all quizzes (instructor view)."""
    _require_instructor(current_user)

    query = db.query(Quiz)
    if course_id:
        query = query.filter(Quiz.course_id == course_id)
    if active_only:
        query = query.filter(Quiz.is_active == True)

    quizzes = query.order_by(desc(Quiz.created_at)).all()

    result = []
    for quiz in quizzes:
        questions = db.query(QuizQuestion).filter(QuizQuestion.quiz_id == quiz.id).all()
        attempts = db.query(QuizAttempt).filter(QuizAttempt.quiz_id == quiz.id).all()

        result.append(QuizListItem(
            id=quiz.id,
            title=quiz.title,
            due_date=quiz.due_date,
            max_attempts=quiz.max_attempts,
            is_active=quiz.is_active,
            question_count=len(questions),
            total_points=sum(q.points for q in questions),
            total_attempts=len(attempts),
        ))

    return result


@router.get("/student", response_model=List[StudentQuiz])
async def get_student_quizzes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get quizzes available to current student."""
    quizzes = db.query(Quiz).filter(Quiz.is_active == True).all()

    result = []
    for quiz in quizzes:
        questions = db.query(QuizQuestion).filter(QuizQuestion.quiz_id == quiz.id).all()
        attempts = db.query(QuizAttempt).filter(
            QuizAttempt.quiz_id == quiz.id,
            QuizAttempt.student_id == current_user.id,
            QuizAttempt.is_submitted == True,
        ).all()

        attempts_used = len(attempts)
        best_score = None
        for attempt in attempts:
            if attempt.score is not None:
                if best_score is None or attempt.score > best_score:
                    best_score = attempt.score

        total_points = sum(q.points for q in questions)

        can_attempt = attempts_used < quiz.max_attempts
        if quiz.due_date and datetime.utcnow() > quiz.due_date:
            can_attempt = False

        result.append(StudentQuiz(
            id=quiz.id,
            title=quiz.title,
            description=quiz.description,
            due_date=quiz.due_date,
            time_limit_minutes=quiz.time_limit_minutes,
            max_attempts=quiz.max_attempts,
            attempts_used=attempts_used,
            best_score=best_score,
            max_score=total_points,
            can_attempt=can_attempt,
            question_count=len(questions),
        ))

    return result


@router.get("/{quiz_id}", response_model=QuizDetailResponse)
async def get_quiz(
    quiz_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get quiz with questions (instructor view, includes correct answers)."""
    _require_instructor(current_user)

    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    questions = db.query(QuizQuestion).filter(
        QuizQuestion.quiz_id == quiz.id
    ).order_by(QuizQuestion.order_index).all()

    total_points = sum(q.points for q in questions)

    return QuizDetailResponse(
        id=quiz.id,
        course_id=quiz.course_id,
        title=quiz.title,
        description=quiz.description,
        time_limit_minutes=quiz.time_limit_minutes,
        max_attempts=quiz.max_attempts,
        due_date=quiz.due_date,
        is_active=quiz.is_active,
        show_answers_after_submit=quiz.show_answers_after_submit,
        question_count=len(questions),
        total_points=total_points,
        created_at=quiz.created_at,
        questions=[
            QuestionResponse(
                id=q.id,
                question_type=q.question_type,
                question_text=q.question_text,
                options=q.options,
                correct_answer=q.correct_answer,
                acceptable_answers=q.acceptable_answers,
                points=q.points,
                order_index=q.order_index,
            )
            for q in questions
        ],
    )


@router.put("/{quiz_id}", response_model=QuizDetailResponse)
async def update_quiz(
    quiz_id: UUID,
    update_data: QuizUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update quiz metadata (instructor only)."""
    _require_instructor(current_user)

    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(quiz, key, value)

    db.commit()
    db.refresh(quiz)

    questions = db.query(QuizQuestion).filter(
        QuizQuestion.quiz_id == quiz.id
    ).order_by(QuizQuestion.order_index).all()
    total_points = sum(q.points for q in questions)

    return QuizDetailResponse(
        id=quiz.id,
        course_id=quiz.course_id,
        title=quiz.title,
        description=quiz.description,
        time_limit_minutes=quiz.time_limit_minutes,
        max_attempts=quiz.max_attempts,
        due_date=quiz.due_date,
        is_active=quiz.is_active,
        show_answers_after_submit=quiz.show_answers_after_submit,
        question_count=len(questions),
        total_points=total_points,
        created_at=quiz.created_at,
        questions=[
            QuestionResponse(
                id=q.id,
                question_type=q.question_type,
                question_text=q.question_text,
                options=q.options,
                correct_answer=q.correct_answer,
                acceptable_answers=q.acceptable_answers,
                points=q.points,
                order_index=q.order_index,
            )
            for q in questions
        ],
    )


@router.delete("/{quiz_id}")
async def delete_quiz(
    quiz_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a quiz (instructor only). Sets inactive instead of hard delete."""
    _require_instructor(current_user)

    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    quiz.is_active = False
    db.commit()

    return {"message": "Quiz deactivated"}


@router.get("/{quiz_id}/results", response_model=List[AttemptListItem])
async def get_quiz_results(
    quiz_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all student attempts for a quiz (instructor only)."""
    _require_instructor(current_user)

    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    attempts = db.query(QuizAttempt).filter(
        QuizAttempt.quiz_id == quiz_id
    ).order_by(desc(QuizAttempt.started_at)).all()

    result = []
    for attempt in attempts:
        student = db.query(User).filter(User.id == attempt.student_id).first()
        answers = db.query(QuizAnswer).filter(QuizAnswer.attempt_id == attempt.id).all()
        has_needs_review = any(a.needs_review for a in answers)

        result.append(AttemptListItem(
            id=attempt.id,
            student_id=attempt.student_id,
            student_name=student.name if student else "Unknown",
            score=attempt.score,
            max_score=attempt.max_score,
            started_at=attempt.started_at,
            submitted_at=attempt.submitted_at,
            is_submitted=attempt.is_submitted,
            needs_review=has_needs_review,
        ))

    return result


@router.put("/answers/{answer_id}/grade")
async def grade_answer(
    answer_id: UUID,
    grade_data: AnswerGrade,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Manually grade a single answer (instructor only)."""
    _require_instructor(current_user)

    answer = db.query(QuizAnswer).filter(QuizAnswer.id == answer_id).first()
    if not answer:
        raise HTTPException(status_code=404, detail="Answer not found")

    answer.is_correct = grade_data.is_correct
    answer.points_awarded = grade_data.points_awarded
    answer.needs_review = False

    # Recalculate attempt score
    attempt = db.query(QuizAttempt).filter(QuizAttempt.id == answer.attempt_id).first()
    if attempt:
        all_answers = db.query(QuizAnswer).filter(QuizAnswer.attempt_id == attempt.id).all()
        attempt.score = sum(a.points_awarded for a in all_answers)

    db.commit()

    return {"message": "Answer graded", "points_awarded": grade_data.points_awarded}


# ---- Student endpoints ----

@router.get("/{quiz_id}/my-attempts", response_model=List[AttemptResponse])
async def get_my_attempts(
    quiz_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get current student's past attempts for a quiz."""
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    attempts = db.query(QuizAttempt).filter(
        QuizAttempt.quiz_id == quiz_id,
        QuizAttempt.student_id == current_user.id,
        QuizAttempt.is_submitted == True,
    ).order_by(desc(QuizAttempt.submitted_at)).all()

    questions = db.query(QuizQuestion).filter(QuizQuestion.quiz_id == quiz_id).all()
    question_map = {q.id: q for q in questions}

    show_answers = quiz.show_answers_after_submit

    result = []
    for attempt in attempts:
        answers = db.query(QuizAnswer).filter(
            QuizAnswer.attempt_id == attempt.id
        ).all()

        answer_results = []
        for answer in answers:
            question = question_map.get(answer.question_id)
            if not question:
                continue
            answer_results.append(AnswerResult(
                question_id=question.id,
                question_text=question.question_text,
                question_type=question.question_type,
                student_answer=answer.student_answer,
                correct_answer=question.correct_answer if show_answers else None,
                is_correct=answer.is_correct,
                points_awarded=answer.points_awarded,
                points_possible=question.points,
                needs_review=answer.needs_review,
            ))

        result.append(AttemptResponse(
            id=attempt.id,
            quiz_id=attempt.quiz_id,
            score=attempt.score or 0,
            max_score=attempt.max_score or 0,
            started_at=attempt.started_at,
            submitted_at=attempt.submitted_at,
            answers=answer_results,
        ))

    return result


@router.get("/{quiz_id}/take", response_model=List[StudentQuestionView])
async def take_quiz(
    quiz_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get quiz questions for taking (no correct answers)."""
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id, Quiz.is_active == True).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    questions = db.query(QuizQuestion).filter(
        QuizQuestion.quiz_id == quiz_id
    ).order_by(QuizQuestion.order_index).all()

    return [
        StudentQuestionView(
            id=q.id,
            question_type=q.question_type,
            question_text=q.question_text,
            options=q.options,
            points=q.points,
            order_index=q.order_index,
        )
        for q in questions
    ]


@router.post("/{quiz_id}/start")
async def start_quiz_attempt(
    quiz_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Start a new quiz attempt."""
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id, Quiz.is_active == True).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    # Check due date
    if quiz.due_date and datetime.utcnow() > quiz.due_date:
        raise HTTPException(status_code=400, detail="Quiz is past due date")

    # Check max attempts
    submitted_attempts = db.query(QuizAttempt).filter(
        QuizAttempt.quiz_id == quiz_id,
        QuizAttempt.student_id == current_user.id,
        QuizAttempt.is_submitted == True,
    ).count()

    if submitted_attempts >= quiz.max_attempts:
        raise HTTPException(status_code=400, detail="Maximum attempts reached")

    # Check for an existing unsubmitted attempt
    existing = db.query(QuizAttempt).filter(
        QuizAttempt.quiz_id == quiz_id,
        QuizAttempt.student_id == current_user.id,
        QuizAttempt.is_submitted == False,
    ).first()

    if existing:
        return {"attempt_id": str(existing.id), "started_at": existing.started_at.isoformat()}

    attempt = QuizAttempt(
        quiz_id=quiz_id,
        student_id=current_user.id,
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)

    return {"attempt_id": str(attempt.id), "started_at": attempt.started_at.isoformat()}


@router.post("/attempts/{attempt_id}/submit", response_model=AttemptResponse)
async def submit_quiz_attempt(
    attempt_id: UUID,
    submission: AttemptSubmit,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Submit answers for a quiz attempt and get auto-graded results."""
    attempt = db.query(QuizAttempt).filter(
        QuizAttempt.id == attempt_id,
        QuizAttempt.student_id == current_user.id,
    ).first()
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")

    if attempt.is_submitted:
        raise HTTPException(status_code=400, detail="Attempt already submitted")

    quiz = db.query(Quiz).filter(Quiz.id == attempt.quiz_id).first()
    questions = db.query(QuizQuestion).filter(QuizQuestion.quiz_id == quiz.id).all()
    question_map = {q.id: q for q in questions}

    # Grade each answer
    answer_records = []
    total_score = 0.0
    max_score = sum(q.points for q in questions)

    # Build lookup of submitted answers
    submitted = {a.question_id: a.student_answer for a in submission.answers}

    for question in questions:
        student_answer = submitted.get(question.id)
        is_correct = None
        points_awarded = 0.0
        needs_review = False

        if student_answer is not None:
            if question.question_type in ("mcq", "true_false"):
                is_correct = student_answer.strip().lower() == question.correct_answer.strip().lower()
                points_awarded = question.points if is_correct else 0

            elif question.question_type == "short_answer":
                answer_lower = student_answer.strip().lower()
                # Check against acceptable answers list
                acceptable = question.acceptable_answers or []
                if acceptable:
                    is_correct = any(
                        kw.strip().lower() in answer_lower
                        for kw in acceptable
                    )
                    # Also check exact match against correct_answer
                    if not is_correct:
                        is_correct = answer_lower == question.correct_answer.strip().lower()
                    points_awarded = question.points if is_correct else 0
                    if not is_correct:
                        needs_review = True
                else:
                    # No acceptable answers defined, check exact match
                    is_correct = answer_lower == question.correct_answer.strip().lower()
                    points_awarded = question.points if is_correct else 0
                    if not is_correct:
                        needs_review = True

        total_score += points_awarded

        answer_record = QuizAnswer(
            attempt_id=attempt.id,
            question_id=question.id,
            student_answer=student_answer,
            is_correct=is_correct,
            points_awarded=points_awarded,
            needs_review=needs_review,
        )
        answer_records.append(answer_record)

    db.add_all(answer_records)

    # Update attempt
    attempt.is_submitted = True
    attempt.submitted_at = datetime.utcnow()
    attempt.score = total_score
    attempt.max_score = max_score

    db.commit()

    # Build response
    show_answers = quiz.show_answers_after_submit
    answer_results = []
    for answer in answer_records:
        question = question_map[answer.question_id]
        answer_results.append(AnswerResult(
            question_id=question.id,
            question_text=question.question_text,
            question_type=question.question_type,
            student_answer=answer.student_answer,
            correct_answer=question.correct_answer if show_answers else None,
            is_correct=answer.is_correct,
            points_awarded=answer.points_awarded,
            points_possible=question.points,
            needs_review=answer.needs_review,
        ))

    return AttemptResponse(
        id=attempt.id,
        quiz_id=attempt.quiz_id,
        score=total_score,
        max_score=max_score,
        started_at=attempt.started_at,
        submitted_at=attempt.submitted_at,
        answers=answer_results,
    )
