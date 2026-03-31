"""Quiz models for knowledge checks."""

from datetime import datetime

from sqlalchemy import Column, String, Text, Boolean, Integer, Float, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.base import UUIDMixin, TimestampMixin


class Quiz(Base, UUIDMixin, TimestampMixin):
    """Quiz model - knowledge check with multiple question types."""

    __tablename__ = "quizzes"

    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    time_limit_minutes = Column(Integer, nullable=True)
    max_attempts = Column(Integer, default=1, nullable=False)
    due_date = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    show_answers_after_submit = Column(Boolean, default=True, nullable=False)

    # Relationships
    course = relationship("Course", backref="quizzes")
    questions = relationship("QuizQuestion", back_populates="quiz", order_by="QuizQuestion.order_index")
    attempts = relationship("QuizAttempt", back_populates="quiz")

    def __repr__(self):
        return f"<Quiz {self.title}>"


class QuizQuestion(Base, UUIDMixin, TimestampMixin):
    """Individual question within a quiz."""

    __tablename__ = "quiz_questions"

    quiz_id = Column(UUID(as_uuid=True), ForeignKey("quizzes.id"), nullable=False)
    question_type = Column(String(20), nullable=False)  # mcq, true_false, short_answer
    question_text = Column(Text, nullable=False)
    options = Column(JSONB, nullable=True)  # ["Option A", "Option B", ...] or ["True", "False"]
    correct_answer = Column(String(500), nullable=False)
    acceptable_answers = Column(JSONB, nullable=True)  # For short answer: ["keyword1", "keyword2"]
    points = Column(Integer, default=1, nullable=False)
    order_index = Column(Integer, default=0, nullable=False)

    # Relationships
    quiz = relationship("Quiz", back_populates="questions")
    answers = relationship("QuizAnswer", back_populates="question")

    def __repr__(self):
        return f"<QuizQuestion {self.question_type}: {self.question_text[:50]}>"


class QuizAttempt(Base, UUIDMixin, TimestampMixin):
    """A student's attempt at a quiz."""

    __tablename__ = "quiz_attempts"

    quiz_id = Column(UUID(as_uuid=True), ForeignKey("quizzes.id"), nullable=False)
    student_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    score = Column(Float, nullable=True)
    max_score = Column(Float, nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    submitted_at = Column(DateTime, nullable=True)
    is_submitted = Column(Boolean, default=False, nullable=False)

    # Relationships
    quiz = relationship("Quiz", back_populates="attempts")
    student = relationship("User", backref="quiz_attempts")
    answers = relationship("QuizAnswer", back_populates="attempt")

    def __repr__(self):
        return f"<QuizAttempt quiz={self.quiz_id} student={self.student_id}>"


class QuizAnswer(Base, UUIDMixin, TimestampMixin):
    """A student's answer to a single question within an attempt."""

    __tablename__ = "quiz_answers"

    attempt_id = Column(UUID(as_uuid=True), ForeignKey("quiz_attempts.id"), nullable=False)
    question_id = Column(UUID(as_uuid=True), ForeignKey("quiz_questions.id"), nullable=False)
    student_answer = Column(Text, nullable=True)
    is_correct = Column(Boolean, nullable=True)
    points_awarded = Column(Float, default=0, nullable=False)
    needs_review = Column(Boolean, default=False, nullable=False)

    # Relationships
    attempt = relationship("QuizAttempt", back_populates="answers")
    question = relationship("QuizQuestion", back_populates="answers")

    def __repr__(self):
        return f"<QuizAnswer question={self.question_id} correct={self.is_correct}>"
