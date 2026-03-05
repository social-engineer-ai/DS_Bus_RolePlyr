"""Pydantic schemas for conversation API."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class StartConversationRequest(BaseModel):
    """Request to start a new conversation."""

    scenario_id: UUID = Field(..., description="ID of the scenario to use")
    context: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        description="Description of the student's model/project",
    )
    assignment_id: Optional[UUID] = Field(
        None, description="Assignment ID if this is a graded attempt"
    )


class SendMessageRequest(BaseModel):
    """Request to send a message in a conversation."""

    content: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="The student's message",
    )


class EndConversationRequest(BaseModel):
    """Request to end a conversation."""

    total_active_seconds: Optional[int] = Field(
        None, description="Total active seconds tracked by frontend timer"
    )


class ViolationRequest(BaseModel):
    """Request to log a screen lock violation."""

    violation_number: int = Field(..., description="Which violation this is (1-4)")
    timestamp: str = Field(..., description="ISO timestamp of the violation")
    turn_number: int = Field(..., description="Current turn number when violation occurred")


class ViolationResponse(BaseModel):
    """Response after logging a violation."""

    violation_count: int
    violation_log: list[dict]


class MessageResponse(BaseModel):
    """Response containing a single message."""

    id: UUID
    role: str  # "student" or "stakeholder"
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationResponse(BaseModel):
    """Response containing conversation details."""

    id: UUID
    scenario_id: UUID
    persona_name: str
    persona_title: str
    mode: str  # "practice" or "graded"
    status: str  # "in_progress", "completed", "abandoned"
    context: str
    turn_count: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    violation_count: int = 0
    violation_log: Optional[list[dict]] = None
    ended_at: Optional[datetime] = None
    total_active_seconds: Optional[int] = None
    messages: list[MessageResponse] = []

    class Config:
        from_attributes = True


class ConversationListItem(BaseModel):
    """Summary of a conversation for list views."""

    id: UUID
    scenario_id: UUID
    persona_name: str
    mode: str
    status: str
    turn_count: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    score: Optional[float] = None  # From grade if exists

    class Config:
        from_attributes = True


class StakeholderMessageResponse(BaseModel):
    """Response after sending a message."""

    student_message: MessageResponse
    stakeholder_message: MessageResponse
    conversation_status: str
    turn_count: int
    should_end: bool = Field(
        False, description="True if conversation has reached max turns"
    )


class EndConversationResponse(BaseModel):
    """Response after ending a conversation."""

    id: UUID
    status: str
    turn_count: int
    completed_at: datetime
    final_message: Optional[MessageResponse] = None


class ScenarioResponse(BaseModel):
    """Response containing scenario details."""

    id: UUID
    name: str
    description: Optional[str]
    persona_name: str
    persona_title: str
    persona_background: Optional[str]
    is_practice: bool
    max_turns: int

    class Config:
        from_attributes = True


class PersonaResponse(BaseModel):
    """Response containing persona details."""

    id: UUID
    name: str
    title: str
    background: Optional[str]
    personality: Optional[str]

    class Config:
        from_attributes = True
