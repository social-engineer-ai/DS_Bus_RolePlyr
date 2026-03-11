"""Pydantic schemas for rubrics, including AI rubric builder."""

from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class CriterionSchema(BaseModel):
    """Schema for a single rubric criterion."""

    name: str
    display_name: str
    description: str = ""
    max_points: int = Field(..., ge=1)
    scoring_guide: Optional[Dict[str, str]] = None


class RubricCreate(BaseModel):
    """Schema for creating a rubric."""

    course_id: UUID
    name: str = Field(..., min_length=1, max_length=255)
    criteria: List[CriterionSchema]


class RubricUpdate(BaseModel):
    """Schema for updating a rubric."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    criteria: Optional[List[CriterionSchema]] = None


class RubricResponse(BaseModel):
    """Response schema for rubric."""

    id: UUID
    course_id: Optional[UUID]
    name: str
    criteria: List[dict]
    total_points: int
    created_at: datetime

    class Config:
        from_attributes = True


class RubricListItem(BaseModel):
    """Simplified rubric for list views."""

    id: UUID
    name: str
    total_points: int
    criteria_count: int
    created_at: datetime


# AI Rubric Builder schemas

class RubricChatMessage(BaseModel):
    """A single message in the rubric builder chat."""

    role: str  # "user" or "assistant"
    content: str


class RubricChatRequest(BaseModel):
    """Request for the AI rubric chat endpoint."""

    messages: List[RubricChatMessage]
    materials_text: str = ""


class RubricDraft(BaseModel):
    """AI-generated rubric draft structure."""

    name: str
    criteria: List[CriterionSchema]


class RubricChatResponse(BaseModel):
    """Response from the AI rubric chat endpoint."""

    reply: str
    rubric_draft: Optional[RubricDraft] = None


class MaterialUploadResponse(BaseModel):
    """Response from the material upload endpoint."""

    extracted_text: str
    filename: str
    pages: Optional[int] = None
