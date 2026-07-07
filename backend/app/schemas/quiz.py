"""Pydantic schemas for quizzes."""

from datetime import datetime
from typing import Optional, List, Any, Dict
from uuid import UUID

from pydantic import BaseModel, Field


# --- Question schemas ---

class QuestionCreate(BaseModel):
    """Schema for creating a question within a quiz."""

    question_type: str = Field(..., pattern="^(mcq|true_false|short_answer|self_authored)$")
    question_text: str = Field(..., min_length=1)
    options: Optional[List[str]] = None
    correct_answer: str = Field(default="instructor_review", min_length=1)
    acceptable_answers: Optional[List[str]] = None
    points: int = Field(default=1, ge=1)
    order_index: int = Field(default=0, ge=0)

    # Rubric-based grading (used by the LLM grader)
    rubric: Optional[List[Dict[str, Any]]] = None
    model_answer: Optional[str] = None
    common_wrong_answers: Optional[str] = None


class QuestionResponse(QuestionCreate):
    """Full question response (instructor view, includes answers)."""

    id: UUID

    class Config:
        from_attributes = True


class StudentQuestionView(BaseModel):
    """Question view for students taking a quiz (no correct answers)."""

    id: UUID
    question_type: str
    question_text: str
    options: Optional[List[str]] = None
    points: int
    order_index: int


# --- Quiz schemas ---

class QuizBase(BaseModel):
    """Base quiz schema."""

    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    time_limit_minutes: Optional[int] = Field(None, ge=1)
    max_attempts: int = Field(default=1, ge=1, le=10)
    due_date: Optional[datetime] = None
    is_active: bool = True
    show_answers_after_submit: bool = True
    require_all_questions: bool = False
    use_llm_grader: bool = False
    llm_grader_model: Optional[str] = None
    grading_instructions: Optional[str] = None
    hw_reference: Optional[str] = None


class QuizCreate(QuizBase):
    """Schema for creating a quiz with questions."""

    course_id: UUID
    questions: List[QuestionCreate] = Field(..., min_length=1)


class QuizUpdate(BaseModel):
    """Schema for updating quiz metadata."""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    time_limit_minutes: Optional[int] = Field(None, ge=1)
    max_attempts: Optional[int] = Field(None, ge=1, le=10)
    due_date: Optional[datetime] = None
    is_active: Optional[bool] = None
    show_answers_after_submit: Optional[bool] = None


class QuizResponse(QuizBase):
    """Response schema for quiz."""

    id: UUID
    course_id: UUID
    question_count: int
    total_points: int
    created_at: datetime

    class Config:
        from_attributes = True


class QuizDetailResponse(QuizResponse):
    """Quiz with all questions (instructor view)."""

    questions: List[QuestionResponse]


class QuizListItem(BaseModel):
    """Simplified quiz for instructor list views."""

    id: UUID
    title: str
    due_date: Optional[datetime]
    max_attempts: int
    is_active: bool
    question_count: int
    total_points: int
    total_attempts: int


class StudentQuiz(BaseModel):
    """Quiz view for students."""

    id: UUID
    title: str
    description: Optional[str]
    due_date: Optional[datetime]
    time_limit_minutes: Optional[int]
    max_attempts: int
    attempts_used: int
    best_score: Optional[float]
    max_score: int
    can_attempt: bool
    question_count: int


# --- Attempt schemas ---

class AnswerSubmit(BaseModel):
    """A single answer submission."""

    question_id: UUID
    student_answer: str


class AttemptSubmit(BaseModel):
    """Submit all answers for a quiz attempt."""

    answers: List[AnswerSubmit]


class AnswerResult(BaseModel):
    """Result for a single answer."""

    id: Optional[UUID] = None  # Answer record UUID (exposed for instructor override)
    question_id: UUID
    question_text: str
    question_type: str
    student_answer: Optional[str]
    correct_answer: Optional[str] = None  # Only if show_answers_after_submit
    is_correct: Optional[bool]
    points_awarded: float
    points_possible: int
    needs_review: bool
    grader_reasoning: Optional[str] = None
    graded_by: str = "none"


class AttemptResponse(BaseModel):
    """Response after submitting a quiz attempt."""

    id: UUID
    quiz_id: UUID
    score: float
    max_score: float
    started_at: datetime
    submitted_at: datetime
    answers: List[AnswerResult]


class AttemptListItem(BaseModel):
    """Attempt summary for instructor results view."""

    id: UUID
    student_id: UUID
    student_name: str
    score: Optional[float]
    max_score: Optional[float]
    started_at: datetime
    submitted_at: Optional[datetime]
    is_submitted: bool
    needs_review: bool


class AnswerGrade(BaseModel):
    """Schema for instructor manual grading of an answer."""

    is_correct: bool
    points_awarded: float = Field(..., ge=0)
