"""Pydantic schemas for assignments."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class AssignmentBase(BaseModel):
    """Base assignment schema."""

    title: str = Field(..., min_length=1, max_length=255)
    instructions: Optional[str] = None
    due_date: Optional[datetime] = None
    max_attempts: int = Field(default=1, ge=1, le=10)
    is_active: bool = True


class AssignmentCreate(AssignmentBase):
    """Schema for creating an assignment."""

    scenario_id: UUID
    course_id: UUID


class AssignmentUpdate(BaseModel):
    """Schema for updating an assignment."""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    instructions: Optional[str] = None
    due_date: Optional[datetime] = None
    max_attempts: Optional[int] = Field(None, ge=1, le=10)
    is_active: Optional[bool] = None


class AssignmentResponse(AssignmentBase):
    """Response schema for assignment."""

    id: UUID
    scenario_id: UUID
    course_id: UUID
    scenario_name: str
    persona_name: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AssignmentListItem(BaseModel):
    """Simplified assignment for list views."""

    id: UUID
    title: str
    scenario_name: str
    persona_name: str
    due_date: Optional[datetime]
    max_attempts: int
    is_active: bool
    total_submissions: int
    graded_submissions: int


class StudentAssignment(BaseModel):
    """Assignment view for students."""

    id: UUID
    title: str
    instructions: Optional[str]
    scenario_name: str
    persona_name: str
    persona_title: str
    due_date: Optional[datetime]
    max_attempts: int
    attempts_used: int
    best_score: Optional[float]
    can_attempt: bool


class AssignmentSubmission(BaseModel):
    """Student's submission record for an assignment."""

    id: UUID
    conversation_id: UUID
    student_id: UUID
    student_name: str
    started_at: datetime
    completed_at: Optional[datetime]
    score: Optional[float]
    status: str
