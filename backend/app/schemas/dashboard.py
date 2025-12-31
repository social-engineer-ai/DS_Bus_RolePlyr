"""Pydantic schemas for dashboard APIs."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class StudentStats(BaseModel):
    """Student's overall statistics."""

    total_conversations: int
    completed_conversations: int
    practice_sessions: int
    graded_sessions: int
    average_score: Optional[float] = None
    best_score: Optional[float] = None
    total_improvement: Optional[float] = None  # First to best score difference


class RecentConversation(BaseModel):
    """Recent conversation for dashboard."""

    id: UUID
    persona_name: str
    status: str
    score: Optional[float] = None
    started_at: datetime
    completed_at: Optional[datetime] = None


class ProgressPoint(BaseModel):
    """A point in the progress chart."""

    date: datetime
    score: float
    conversation_id: UUID
    persona_name: str


class StudentDashboard(BaseModel):
    """Full student dashboard data."""

    stats: StudentStats
    recent_conversations: list[RecentConversation]
    progress_history: list[ProgressPoint]
    recommended_scenario: Optional[str] = None


class StudentSummary(BaseModel):
    """Summary of a student for instructor view."""

    id: UUID
    name: str
    email: str
    total_conversations: int
    average_score: Optional[float] = None
    last_active: Optional[datetime] = None
    needs_attention: bool = False


class ClassStats(BaseModel):
    """Class-wide statistics for instructor."""

    total_students: int
    active_students: int  # Had activity in last 7 days
    total_conversations: int
    total_graded: int
    average_score: Optional[float] = None
    score_distribution: dict[str, int]  # "90-100": 5, "80-89": 10, etc.
    common_struggles: list[str]


class GradeForReview(BaseModel):
    """Grade needing instructor review."""

    id: UUID
    conversation_id: UUID
    student_name: str
    persona_name: str
    score: float
    ai_confidence: float
    graded_at: datetime


class InstructorDashboard(BaseModel):
    """Full instructor dashboard data."""

    class_stats: ClassStats
    recent_activity: list[RecentConversation]
    students: list[StudentSummary]
    grades_needing_review: list[GradeForReview]
