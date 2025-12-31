"""Persona model for stakeholder simulation."""

from sqlalchemy import Column, String, Text, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.base import UUIDMixin, TimestampMixin


class Persona(Base, UUIDMixin, TimestampMixin):
    """Stakeholder persona model."""

    __tablename__ = "personas"

    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id"), nullable=True)
    name = Column(String(255), nullable=False)
    title = Column(String(255), nullable=False)
    background = Column(Text, nullable=True)
    personality = Column(Text, nullable=True)
    concerns = Column(JSONB, nullable=True)  # List of concerns to probe
    required_questions = Column(JSONB, nullable=True)  # Questions persona must ask
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    course = relationship("Course", back_populates="personas")
    scenarios = relationship("Scenario", back_populates="persona")

    def __repr__(self):
        return f"<Persona {self.name} - {self.title}>"

    def to_prompt_context(self) -> dict:
        """Convert persona to context for LLM prompts."""
        return {
            "name": self.name,
            "title": self.title,
            "background": self.background or "",
            "personality": self.personality or "",
            "concerns": self.concerns or [],
            "required_questions": self.required_questions or [],
        }
