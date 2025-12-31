"""Scenario model combining persona, rubric, and settings."""

from sqlalchemy import Column, String, Text, Boolean, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.base import UUIDMixin, TimestampMixin


class Scenario(Base, UUIDMixin, TimestampMixin):
    """Scenario model - combines persona, rubric, and conversation settings."""

    __tablename__ = "scenarios"

    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id"), nullable=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    persona_id = Column(UUID(as_uuid=True), ForeignKey("personas.id"), nullable=False)
    rubric_id = Column(UUID(as_uuid=True), ForeignKey("rubrics.id"), nullable=False)
    is_practice = Column(Boolean, default=True, nullable=False)
    max_turns = Column(Integer, default=15, nullable=False)

    # Relationships
    course = relationship("Course", back_populates="scenarios")
    persona = relationship("Persona", back_populates="scenarios")
    rubric = relationship("Rubric", back_populates="scenarios")
    assignments = relationship("Assignment", back_populates="scenario")
    conversations = relationship("Conversation", back_populates="scenario")

    def __repr__(self):
        return f"<Scenario {self.name}>"
