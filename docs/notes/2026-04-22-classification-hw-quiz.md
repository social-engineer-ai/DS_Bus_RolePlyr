# BADM 576 Classification HW Quiz — LLM Grader & Auto-Grade-on-Submit

**Date:** 2026-04-22
**Status:** Live in production, ~44 attempts from ~29 students logged on day-one.

## Outcome

Built a rubric-driven, LLM-graded quiz feature on top of the existing quiz system. Students take a short-answer quiz, their answers are auto-graded by Claude Opus 4.7 on submit, and all grades are flagged `needs_review` so the instructor confirms or overrides each one. Deployed and used the same day for BADM 576 session 5.

**Live quiz ID:** `3467222f-c7c2-4263-94f7-d004ce5cd474`
Instructor results URL: http://3.90.88.174:3002/instructor/quizzes/3467222f-c7c2-4263-94f7-d004ce5cd474/results

## The quiz itself

**Title:** BADM 576 — Classification HW Quiz
**Format:** 5 short-answer questions, 4 points each, 20 points total, 10 min timer, 3 attempts (best score counts, each attempt tracked independently). Serves as a multiplier on the Classification HW grade.

### Questions (in brief)

1. **Explanatory vs predictive + bias/variance** — identify (a) fairness audit and (b) HR-review automation; explain why the distinction matters for what you optimize.
2. **Omitted variable bias** — gender coefficient changed when `avg_training_score` was dropped; use "holding all else constant".
3. **The 0.5 cutoff trap** — hidden cost-equality assumption; why wrong for Sophia (FN=$1000, FP=$500); direction of optimal cutoff.
4. **Cutoff direction shift** — why a lower FN cost moves the optimal cutoff *higher* (non-obvious; the common mistake reverses the logic).
5. **Hyperparameter mechanism** — for `min_samples_split` and `max_depth`: (a) what each controls, (b) what happens to the tree and why that changes over/underfit risk when you make them more restrictive.

### Rubric principle (5-tier per question, 4/3/2/1/0)

- **Reward understanding expressed in plain language.** If the student describes the correct concept in their own words, give full credit even without technical terms.
- **Credit the understanding, not the vocabulary.** When technical terms appear, look for evidence the student understands what the terms mean.
- **Partial credit is expected**, not exceptional.
- **Common-wrong-answer warnings** are embedded per question so the grader doesn't get tricked by fluent-sounding but reversed-direction answers (especially Q3, Q4, and Q5's "they control overfitting" trap).

## Architecture decisions

### 1. LLM grader runs at submit (auto), not on-demand

Initial design deferred grading until instructor click — safer for piloting but surprised students with 0/20 on submit. After Alex Chen's first test submission, flipped to auto-grade-on-submit when `use_llm_grader=true`. Trade-off: submit now takes ~15–30s (5 Opus calls in parallel); graceful fallback if grader errors — attempt still saves with needs_review=true so instructor can re-trigger.

### 2. Opus 4.7 is the default grader model

Called per-quiz via `llm_grader_model` column (defaults to `claude-opus-4-7`). The shared `LLMClient` automatically drops the `temperature` param for Opus 4.7 because the API deprecated it — Sonnet/Haiku callers are unaffected.

### 3. `needs_review=true` stays until the instructor confirms

LLM is not authoritative. Every LLM grade sits as "[tier] reasoning…" with `graded_by='llm'` until the instructor uses the review UI to accept or override (which writes `graded_by='instructor'` and flips `needs_review=false`).

### 4. Scoring: all questions required, max_score = 20 fixed

New `require_all_questions` flag on Quiz. When true, max_score = sum of question points regardless of how many the student answered — skipping a question costs points rather than shrinking the denominator. Legacy "answer any 5" behavior is preserved for other quizzes where `require_all_questions=false`.

### 5. Tone: constructive, not punitive

Grading instructions sent to the LLM reward plain-language understanding; they do not instruct the model to "penalize terminology-without-understanding" — that wording was considered and rejected per user feedback. Current framing: "Reward understanding expressed in plain language … when a student uses technical terms, look for evidence they understand what the terms mean and credit the understanding, not the vocabulary alone."

## What was built

### Backend

- **`backend/alembic/versions/003_add_llm_grading.py`** — migration adding:
  - `quizzes`: `require_all_questions`, `use_llm_grader`, `llm_grader_model`, `grading_instructions`, `hw_reference`
  - `quiz_questions`: `rubric` (JSONB tier list), `model_answer`, `common_wrong_answers`
  - `quiz_answers`: `grader_reasoning`, `graded_by` enum (`none`/`llm`/`instructor`)
- **`backend/app/services/quiz_grader.py`** — async grader. For each needs-review answer, builds a prompt from `{quiz.grading_instructions, question.rubric, question.model_answer, question.common_wrong_answers, student_answer}`, calls Opus 4.7 with JSON output `{points_awarded, tier, reasoning}`, persists it. Up to 5 concurrent calls per attempt via asyncio semaphore. Graceful per-answer error handling.
- **`backend/app/routers/quizzes.py`** — new endpoints:
  - `POST /attempts/{id}/grade-with-llm` (single attempt)
  - `POST /quizzes/{id}/grade-all-with-llm` (bulk)
  - `GET /attempts/{id}` (instructor detail view with reasoning)
  - Modified `submit_quiz_attempt` to auto-run grader when `use_llm_grader=true`
  - Modified `grade_answer` to record `graded_by='instructor'` on override
- **`backend/app/services/llm_client.py`** — accepts `temperature=None`; automatically drops temperature for Opus 4.7 to handle the API deprecation.
- **`backend/app/schemas/quiz.py`** — schemas carry new fields; `AnswerResult` exposes `id` (needed for inline override), `grader_reasoning`, `graded_by`.

### Frontend

- **`frontend/src/app/instructor/quizzes/[id]/results/page.tsx`** — new review page. Lists all attempts with `needs_review` badges, has a "Grade all with LLM" bulk button and a per-attempt review panel showing:
  - Student's answer verbatim
  - LLM reasoning (blue box) with tier label
  - Collapsible model answer
  - Points input + "Save grade / Confirm / override" button that calls the manual grade endpoint
- **`frontend/src/lib/api.ts`** — `getAttemptDetail`, `gradeAttemptWithLLM`, `gradeAllAttemptsWithLLM`; `AnswerResult` TS interface updated.

### Setup script

- **`setup_576_classification_quiz.py`** — creates the quiz with all 5 questions, full rubric, model answers, common-wrong-answers, grading instructions, HW reference, Opus 4.7 grader, all-required scoring, 3 attempts, 10-min limit, 7-day due date.

## Day-one results snapshot

- **44 attempts from ~29 real students** + 1 test account.
- Median ≈ 13.5/20. Top quartile 15+. Eight students scored 16+. Six early submissions recorded 0.0/20 — five were submitted before auto-grade-on-submit was deployed or were blank; all of those students have later attempts that graded properly (retry model is working as intended — first attempt 0 → later attempt 13+).
- All attempts flagged `needs_review=true` pending instructor confirmation.

## Follow-up work

- **`/new-quiz` authoring slash command** — reusable interview flow so the instructor can bring a new quiz document and Claude walks them through building the question/rubric/grader config. Scoped in the architecture discussion but not yet built.
- **Editing existing quiz questions via API** — currently editing requires delete-and-recreate. A `PUT /quizzes/{id}/questions/{question_id}` endpoint would let us replace a question without losing the quiz ID / old attempts.
- **Direct-to-quiz deep link** — no `/quizzes/{id}/take` link yet; students navigate via the quiz list.
- **Investigating the six 0.0 submissions** — user flagged whether those were blank submits or grader errors; not yet inspected.
