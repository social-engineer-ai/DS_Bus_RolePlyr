"""Pydantic schemas for scenarios."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ScenarioCreate(BaseModel):
    """Schema for creating a scenario."""

    course_id: UUID
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    persona_id: UUID
    rubric_id: UUID
    is_practice: bool = True
    max_turns: int = Field(default=15, ge=1, le=50)


class ScenarioUpdate(BaseModel):
    """Schema for updating a scenario."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    persona_id: Optional[UUID] = None
    rubric_id: Optional[UUID] = None
    is_practice: Optional[bool] = None
    max_turns: Optional[int] = Field(None, ge=1, le=50)


class ScenarioResponse(BaseModel):
    """Response schema for scenario."""

    id: UUID
    course_id: Optional[UUID]
    name: str
    description: Optional[str]
    persona_id: UUID
    rubric_id: UUID
    persona_name: str
    rubric_name: str
    is_practice: bool
    max_turns: int
    created_at: datetime

    class Config:
        from_attributes = True


class ScenarioListItem(BaseModel):
    """Simplified scenario for list views."""

    id: UUID
    name: str
    persona_name: str
    rubric_name: str
    is_practice: bool
    max_turns: int
    created_at: datetime
