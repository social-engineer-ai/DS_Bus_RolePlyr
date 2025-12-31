"""Grade model for conversation evaluation."""

from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, Enum as SQLEnum, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.database import Base
from app.models.base import UUIDMixin


class GradedBy(str, enum.Enum):
    """Who graded the conversation."""

    AI = "ai"
    INSTRUCTOR = "instructor"


class Grade(Base, UUIDMixin):
    """Grade for a completed conversation.

    criteria_scores format:
    {
        "business_value_articulation": {
            "score": 20,
            "max_score": 25,
            "evidence": "Student mentioned cost savings...",
            "feedback": "Good quantification but..."
        },
        ...
    }
    """

    __tablename__ = "grades"

    conversation_id = Column(
        UUID(as_uuid=True), ForeignKey("conversations.id"), unique=True, nullable=False
    )
    rubric_id = Column(UUID(as_uuid=True), ForeignKey("rubrics.id"), nullable=False)
    criteria_scores = Column(JSONB, nullable=False)
    total_score = Column(Numeric(5, 2), nullable=False)
    overall_feedback = Column(Text, nullable=True)
    strengths = Column(JSONB, nullable=True)  # List of strengths
    areas_for_improvement = Column(JSONB, nullable=True)  # List of areas to improve
    ai_confidence = Column(Numeric(3, 2), nullable=True)  # 0.00 - 1.00
    graded_by = Column(SQLEnum(GradedBy), nullable=False, default=GradedBy.AI)
    instructor_override = Column(Boolean, default=False, nullable=False)
    override_reason = Column(Text, nullable=True)
    graded_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    conversation = relationship("Conversation", back_populates="grade")
    rubric = relationship("Rubric", back_populates="grades")

    def __repr__(self):
        return f"<Grade {self.total_score} ({self.graded_by.value})>"

    @property
    def needs_review(self) -> bool:
        """Check if grade needs instructor review based on AI confidence."""
        if self.ai_confidence is None:
            return True
        return float(self.ai_confidence) < 0.7
