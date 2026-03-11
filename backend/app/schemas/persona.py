"""Pydantic schemas for personas."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class PersonaCreate(BaseModel):
    """Schema for creating a persona."""

    course_id: UUID
    name: str = Field(..., min_length=1, max_length=255)
    title: str = Field(..., min_length=1, max_length=255)
    background: Optional[str] = None
    personality: Optional[str] = None
    concerns: Optional[List[str]] = None
    required_questions: Optional[List[str]] = None


class PersonaUpdate(BaseModel):
    """Schema for updating a persona."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    background: Optional[str] = None
    personality: Optional[str] = None
    concerns: Optional[List[str]] = None
    required_questions: Optional[List[str]] = None


class PersonaResponse(BaseModel):
    """Response schema for persona."""

    id: UUID
    course_id: Optional[UUID]
    name: str
    title: str
    background: Optional[str]
    personality: Optional[str]
    concerns: Optional[List[str]]
    required_questions: Optional[List[str]]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class PersonaListItem(BaseModel):
    """Simplified persona for list views."""

    id: UUID
    name: str
    title: str
    is_active: bool
    created_at: datetime
