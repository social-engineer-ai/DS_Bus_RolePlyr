"""Dashboard API endpoints."""

from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, UserRole
from app.models.conversation import Conversation, ConversationStatus, ConversationMode
from app.models.scenario import Scenario
from app.models.persona import Persona
from app.models.grade import Grade
from app.schemas.dashboard import (
    StudentStats,
    StudentDashboard,
    RecentConversation,
    ProgressPoint,
    InstructorDashboard,
    ClassStats,
    StudentSummary,
    GradeForReview,
)
from app.routers.auth import MOCK_USERS

router = APIRouter()


def get_current_user_id(user_key: Optional[str] = None) -> UUID:
    """Get current user ID from mock auth."""
    if not user_key:
        user_key = "student1"
    user = MOCK_USERS.get(user_key)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user")
    return UUID(user["id"])


def get_user_role(user_key: Optional[str] = None) -> str:
    """Get current user's role."""
    if not user_key:
        user_key = "student1"
    user = MOCK_USERS.get(user_key)
    return user["role"] if user else "student"


@router.get("/student", response_model=StudentDashboard)
async def get_student_dashboard(
    db: Session = Depends(get_db),
    user_key: Optional[str] = None,
):
    """Get student dashboard with stats and recent activity."""
    user_id = get_current_user_id(user_key)

    # Get all conversations
    conversations = (
        db.query(Conversation)
        .filter(Conversation.user_id == user_id)
        .all()
    )

    # Calculate stats
    total = len(conversations)
    completed = len([c for c in conversations if c.status == ConversationStatus.COMPLETED])
    practice = len([c for c in conversations if c.mode == ConversationMode.PRACTICE])
    graded = len([c for c in conversations if c.mode == ConversationMode.GRADED])

    # Get scores
    scores = []
    for conv in conversations:
        if conv.grade:
            scores.append(float(conv.grade.total_score))

    avg_score = sum(scores) / len(scores) if scores else None
    best_score = max(scores) if scores else None

    # Calculate improvement (first graded vs best)
    improvement = None
    if len(scores) >= 2:
        # Get first score chronologically
        graded_convs = sorted(
            [c for c in conversations if c.grade],
            key=lambda x: x.started_at
        )
        if graded_convs:
            first_score = float(graded_convs[0].grade.total_score)
            improvement = best_score - first_score

    stats = StudentStats(
        total_conversations=total,
        completed_conversations=completed,
        practice_sessions=practice,
        graded_sessions=graded,
        average_score=round(avg_score, 1) if avg_score else None,
        best_score=round(best_score, 1) if best_score else None,
        total_improvement=round(improvement, 1) if improvement else None,
    )

    # Recent conversations
    recent_convs = (
        db.query(Conversation)
        .filter(Conversation.user_id == user_id)
        .order_by(desc(Conversation.started_at))
        .limit(5)
        .all()
    )

    recent = []
    for conv in recent_convs:
        scenario = db.query(Scenario).filter(Scenario.id == conv.scenario_id).first()
        persona = db.query(Persona).filter(Persona.id == scenario.persona_id).first() if scenario else None

        recent.append(RecentConversation(
            id=conv.id,
            persona_name=persona.name if persona else "Unknown",
            status=conv.status.value,
            score=float(conv.grade.total_score) if conv.grade else None,
            started_at=conv.started_at,
            completed_at=conv.completed_at,
        ))

    # Progress history (for chart)
    progress = []
    graded_conversations = (
        db.query(Conversation)
        .filter(Conversation.user_id == user_id)
        .filter(Conversation.status == ConversationStatus.COMPLETED)
        .join(Grade)
        .order_by(Conversation.completed_at)
        .all()
    )

    for conv in graded_conversations:
        if conv.grade and conv.completed_at:
            scenario = db.query(Scenario).filter(Scenario.id == conv.scenario_id).first()
            persona = db.query(Persona).filter(Persona.id == scenario.persona_id).first() if scenario else None

            progress.append(ProgressPoint(
                date=conv.completed_at,
                score=float(conv.grade.total_score),
                conversation_id=conv.id,
                persona_name=persona.name if persona else "Unknown",
            ))

    return StudentDashboard(
        stats=stats,
        recent_conversations=recent,
        progress_history=progress,
        recommended_scenario=None,  # Could add recommendation logic
    )


@router.get("/instructor", response_model=InstructorDashboard)
async def get_instructor_dashboard(
    db: Session = Depends(get_db),
    user_key: Optional[str] = None,
):
    """Get instructor dashboard with class overview."""
    role = get_user_role(user_key)

    if role not in ["instructor", "admin"]:
        raise HTTPException(status_code=403, detail="Instructor access required")

    # Get all students
    students = db.query(User).filter(User.role == UserRole.STUDENT).all()

    # Get all conversations
    all_conversations = db.query(Conversation).all()

    # Calculate class stats
    week_ago = datetime.utcnow() - timedelta(days=7)
    active_student_ids = set(
        c.user_id for c in all_conversations
        if c.started_at >= week_ago
    )

    # Score distribution
    grades = db.query(Grade).all()
    scores = [float(g.total_score) for g in grades]

    distribution = {
        "90-100": 0,
        "80-89": 0,
        "70-79": 0,
        "60-69": 0,
        "Below 60": 0,
    }

    for score in scores:
        if score >= 90:
            distribution["90-100"] += 1
        elif score >= 80:
            distribution["80-89"] += 1
        elif score >= 70:
            distribution["70-79"] += 1
        elif score >= 60:
            distribution["60-69"] += 1
        else:
            distribution["Below 60"] += 1

    # Common struggles (simplified - could use AI analysis)
    common_struggles = []
    low_score_criteria = {}
    for grade in grades:
        for criterion, data in grade.criteria_scores.items():
            score_pct = data.get("score", 0) / data.get("max_score", 1) * 100
            if score_pct < 70:
                low_score_criteria[criterion] = low_score_criteria.get(criterion, 0) + 1

    # Get top 3 struggles
    sorted_struggles = sorted(low_score_criteria.items(), key=lambda x: x[1], reverse=True)
    criterion_names = {
        "business_value_articulation": "Quantifying business value",
        "audience_adaptation": "Adapting to audience",
        "handling_objections": "Handling objections",
        "clarity_and_structure": "Clear structure",
        "honesty_and_limitations": "Discussing limitations",
        "actionable_recommendation": "Clear recommendations",
    }
    for criterion, count in sorted_struggles[:3]:
        if count > 0:
            common_struggles.append(criterion_names.get(criterion, criterion))

    class_stats = ClassStats(
        total_students=len(students),
        active_students=len(active_student_ids),
        total_conversations=len(all_conversations),
        total_graded=len(grades),
        average_score=round(sum(scores) / len(scores), 1) if scores else None,
        score_distribution=distribution,
        common_struggles=common_struggles,
    )

    # Recent activity
    recent_activity = (
        db.query(Conversation)
        .order_by(desc(Conversation.started_at))
        .limit(10)
        .all()
    )

    recent = []
    for conv in recent_activity:
        scenario = db.query(Scenario).filter(Scenario.id == conv.scenario_id).first()
        persona = db.query(Persona).filter(Persona.id == scenario.persona_id).first() if scenario else None

        recent.append(RecentConversation(
            id=conv.id,
            persona_name=persona.name if persona else "Unknown",
            status=conv.status.value,
            score=float(conv.grade.total_score) if conv.grade else None,
            started_at=conv.started_at,
            completed_at=conv.completed_at,
        ))

    # Student summaries
    student_summaries = []
    for student in students:
        student_convs = [c for c in all_conversations if c.user_id == student.id]
        student_scores = [
            float(c.grade.total_score) for c in student_convs if c.grade
        ]

        last_conv = max(student_convs, key=lambda x: x.started_at) if student_convs else None

        # Flag students with low scores or no recent activity
        needs_attention = False
        if student_scores and sum(student_scores) / len(student_scores) < 60:
            needs_attention = True
        if not last_conv or last_conv.started_at < week_ago:
            needs_attention = True

        student_summaries.append(StudentSummary(
            id=student.id,
            name=student.name,
            email=student.email,
            total_conversations=len(student_convs),
            average_score=round(sum(student_scores) / len(student_scores), 1) if student_scores else None,
            last_active=last_conv.started_at if last_conv else None,
            needs_attention=needs_attention,
        ))

    # Sort by needs attention first, then by name
    student_summaries.sort(key=lambda x: (not x.needs_attention, x.name))

    # Grades needing review
    low_confidence_grades = (
        db.query(Grade)
        .filter(Grade.ai_confidence < 0.7)
        .filter(Grade.instructor_override == False)
        .order_by(desc(Grade.graded_at))
        .limit(10)
        .all()
    )

    grades_for_review = []
    for grade in low_confidence_grades:
        conv = db.query(Conversation).filter(Conversation.id == grade.conversation_id).first()
        if conv:
            student = db.query(User).filter(User.id == conv.user_id).first()
            scenario = db.query(Scenario).filter(Scenario.id == conv.scenario_id).first()
            persona = db.query(Persona).filter(Persona.id == scenario.persona_id).first() if scenario else None

            grades_for_review.append(GradeForReview(
                id=grade.id,
                conversation_id=grade.conversation_id,
                student_name=student.name if student else "Unknown",
                persona_name=persona.name if persona else "Unknown",
                score=float(grade.total_score),
                ai_confidence=float(grade.ai_confidence) if grade.ai_confidence else 0,
                graded_at=grade.graded_at,
            ))

    return InstructorDashboard(
        class_stats=class_stats,
        recent_activity=recent,
        students=student_summaries,
        grades_needing_review=grades_for_review,
    )
