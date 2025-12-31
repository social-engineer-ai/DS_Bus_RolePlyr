"""Pydantic schemas for grading API."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class CriterionScore(BaseModel):
    """Score for a single rubric criterion."""

    score: float
    max_score: float
    evidence: str
    feedback: str


class GradeResponse(BaseModel):
    """Full grade response with all details."""

    id: UUID
    conversation_id: UUID
    rubric_id: UUID
    criteria_scores: dict[str, CriterionScore]
    total_score: float
    max_score: float = 100
    overall_feedback: str
    strengths: list[str]
    areas_for_improvement: list[str]
    ai_confidence: Optional[float] = None
    graded_by: str  # "ai" or "instructor"
    instructor_override: bool = False
    override_reason: Optional[str] = None
    graded_at: datetime
    needs_review: bool = False

    class Config:
        from_attributes = True


class GradeSummary(BaseModel):
    """Brief grade summary for list views."""

    id: UUID
    conversation_id: UUID
    total_score: float
    max_score: float = 100
    graded_by: str
    graded_at: datetime
    needs_review: bool = False

    class Config:
        from_attributes = True


class GradeOverrideRequest(BaseModel):
    """Request to override a grade."""

    criterion_name: str = Field(..., description="Name of criterion to override")
    new_score: float = Field(..., ge=0, description="New score for the criterion")
    reason: str = Field(..., min_length=10, description="Reason for override")


class FullGradeOverrideRequest(BaseModel):
    """Request to override the entire grade."""

    criteria_scores: dict[str, float] = Field(
        ..., description="New scores for each criterion"
    )
    reason: str = Field(..., min_length=10, description="Reason for override")


class RubricCriterion(BaseModel):
    """A single criterion in a rubric."""

    name: str
    display_name: str
    description: str
    max_points: int
    scoring_guide: dict[str, str]


class RubricResponse(BaseModel):
    """Full rubric response."""

    id: UUID
    name: str
    criteria: list[RubricCriterion]
    total_points: int

    class Config:
        from_attributes = True


class TriggerGradeRequest(BaseModel):
    """Request to manually trigger grading."""

    force: bool = Field(
        False, description="Force re-grading even if grade exists"
    )
