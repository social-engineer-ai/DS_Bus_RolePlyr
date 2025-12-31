"""Assignment model for graded scenarios."""

from sqlalchemy import Column, String, Text, Boolean, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.base import UUIDMixin, TimestampMixin


class Assignment(Base, UUIDMixin, TimestampMixin):
    """Assignment model - graded scenario with due date and attempt limits."""

    __tablename__ = "assignments"

    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id"), nullable=False)
    scenario_id = Column(UUID(as_uuid=True), ForeignKey("scenarios.id"), nullable=False)
    title = Column(String(255), nullable=False)
    instructions = Column(Text, nullable=True)
    due_date = Column(DateTime, nullable=True)
    max_attempts = Column(Integer, default=1, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    course = relationship("Course", back_populates="assignments")
    scenario = relationship("Scenario", back_populates="assignments")
    conversations = relationship("Conversation", back_populates="assignment")

    def __repr__(self):
        return f"<Assignment {self.title}>"
