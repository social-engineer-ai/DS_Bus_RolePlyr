"""Conversation and Message models."""

from datetime import datetime

from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from app.database import Base
from app.models.base import UUIDMixin, TimestampMixin


class ConversationMode(str, enum.Enum):
    """Conversation mode."""

    PRACTICE = "practice"
    GRADED = "graded"


class ConversationStatus(str, enum.Enum):
    """Conversation status."""

    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class MessageRole(str, enum.Enum):
    """Message sender role."""

    STUDENT = "student"
    STAKEHOLDER = "stakeholder"


class Conversation(Base, UUIDMixin):
    """Conversation model - a role-play session."""

    __tablename__ = "conversations"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    scenario_id = Column(UUID(as_uuid=True), ForeignKey("scenarios.id"), nullable=False)
    assignment_id = Column(UUID(as_uuid=True), ForeignKey("assignments.id"), nullable=True)
    context = Column(Text, nullable=True)  # Student's model description
    mode = Column(SQLEnum(ConversationMode), nullable=False, default=ConversationMode.PRACTICE)
    status = Column(
        SQLEnum(ConversationStatus), nullable=False, default=ConversationStatus.IN_PROGRESS
    )
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    turn_count = Column(Integer, default=0, nullable=False)

    # Relationships
    user = relationship("User", back_populates="conversations")
    scenario = relationship("Scenario", back_populates="conversations")
    assignment = relationship("Assignment", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", order_by="Message.created_at")
    grade = relationship("Grade", back_populates="conversation", uselist=False)

    def __repr__(self):
        return f"<Conversation {self.id} ({self.status.value})>"

    def to_transcript(self) -> str:
        """Convert conversation to transcript format for grading."""
        lines = []
        for msg in self.messages:
            role = "Student" if msg.role == MessageRole.STUDENT else "Stakeholder"
            lines.append(f"{role}: {msg.content}")
        return "\n\n".join(lines)


class Message(Base, UUIDMixin, TimestampMixin):
    """Message within a conversation."""

    __tablename__ = "messages"

    conversation_id = Column(
        UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False
    )
    role = Column(SQLEnum(MessageRole), nullable=False)
    content = Column(Text, nullable=False)

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")

    def __repr__(self):
        preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"<Message {self.role.value}: {preview}>"
