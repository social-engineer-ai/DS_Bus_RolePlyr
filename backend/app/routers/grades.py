"""Grading API endpoints."""

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.conversation import Conversation, ConversationStatus
from app.models.scenario import Scenario
from app.models.persona import Persona
from app.models.rubric import Rubric
from app.models.grade import Grade, GradedBy
from app.models.user import User
from app.schemas.grade import (
    GradeResponse,
    GradeSummary,
    GradeOverrideRequest,
    FullGradeOverrideRequest,
    RubricResponse,
    TriggerGradeRequest,
    CriterionScore,
)
from app.services.grading_engine import GradingEngine
from app.routers.auth import get_current_user

router = APIRouter()


def _grade_to_response(grade: Grade, rubric: Rubric, conversation: Conversation = None) -> GradeResponse:
    """Convert Grade model to response schema."""
    criteria_scores = {}
    for name, data in grade.criteria_scores.items():
        criteria_scores[name] = CriterionScore(
            score=data.get("score", 0),
            max_score=data.get("max_score", 0),
            evidence=data.get("evidence", ""),
            feedback=data.get("feedback", ""),
        )

    resp = GradeResponse(
        id=grade.id,
        conversation_id=grade.conversation_id,
        rubric_id=grade.rubric_id,
        criteria_scores=criteria_scores,
        total_score=float(grade.total_score),
        max_score=rubric.total_points,
        overall_feedback=grade.overall_feedback or "",
        strengths=grade.strengths or [],
        areas_for_improvement=grade.areas_for_improvement or [],
        ai_confidence=float(grade.ai_confidence) if grade.ai_confidence else None,
        graded_by=grade.graded_by.value,
        instructor_override=grade.instructor_override,
        override_reason=grade.override_reason,
        graded_at=grade.graded_at,
        needs_review=grade.needs_review,
    )

    if conversation:
        resp.violation_count = conversation.violation_count
        resp.violation_log = conversation.violation_log
        resp.total_active_seconds = conversation.total_active_seconds
        resp.ended_at = conversation.ended_at

    return resp


async def _perform_grading(
    conversation_id: UUID,
    db: Session,
) -> Grade:
    """Perform grading for a conversation."""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()

    if not conversation:
        raise ValueError("Conversation not found")

    if conversation.status != ConversationStatus.COMPLETED:
        raise ValueError("Can only grade completed conversations")

    scenario = db.query(Scenario).filter(
        Scenario.id == conversation.scenario_id
    ).first()

    persona = db.query(Persona).filter(
        Persona.id == scenario.persona_id
    ).first()

    rubric = db.query(Rubric).filter(
        Rubric.id == scenario.rubric_id
    ).first()

    if not all([scenario, persona, rubric]):
        raise ValueError("Missing scenario, persona, or rubric")

    engine = GradingEngine(rubric)
    grade_data = await engine.grade_conversation(conversation, persona)

    grade = engine.create_grade_record(
        conversation_id=conversation.id,
        rubric_id=rubric.id,
        grade_data=grade_data,
    )

    db.add(grade)
    db.commit()
    db.refresh(grade)

    return grade


@router.get("/conversations/{conversation_id}", response_model=GradeResponse)
async def get_grade(
    conversation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get the grade for a conversation."""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if current_user.role.value == "student" and conversation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    grade = db.query(Grade).filter(
        Grade.conversation_id == conversation_id
    ).first()

    if not grade:
        raise HTTPException(status_code=404, detail="Grade not found")

    rubric = db.query(Rubric).filter(Rubric.id == grade.rubric_id).first()

    return _grade_to_response(grade, rubric, conversation)


@router.post("/conversations/{conversation_id}/grade", response_model=GradeResponse)
async def trigger_grading(
    conversation_id: UUID,
    request: TriggerGradeRequest = TriggerGradeRequest(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Manually trigger grading for a conversation."""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if current_user.role.value == "student" and conversation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    if conversation.status != ConversationStatus.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail="Can only grade completed conversations"
        )

    existing_grade = db.query(Grade).filter(
        Grade.conversation_id == conversation_id
    ).first()

    if existing_grade and not request.force:
        rubric = db.query(Rubric).filter(Rubric.id == existing_grade.rubric_id).first()
        return _grade_to_response(existing_grade, rubric, conversation)

    if existing_grade and request.force:
        db.delete(existing_grade)
        db.commit()

    try:
        grade = await _perform_grading(conversation_id, db)
        rubric = db.query(Rubric).filter(Rubric.id == grade.rubric_id).first()
        return _grade_to_response(grade, rubric, conversation)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Grading failed: {str(e)}")


@router.post(
    "/conversations/{conversation_id}/override",
    response_model=GradeResponse
)
async def override_grade(
    conversation_id: UUID,
    request: FullGradeOverrideRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Override grades (instructor only)."""
    if current_user.role.value not in ["instructor", "admin"]:
        raise HTTPException(
            status_code=403,
            detail="Only instructors can override grades"
        )

    grade = db.query(Grade).filter(
        Grade.conversation_id == conversation_id
    ).first()

    if not grade:
        raise HTTPException(status_code=404, detail="Grade not found")

    rubric = db.query(Rubric).filter(Rubric.id == grade.rubric_id).first()

    criterion_names = {c["name"] for c in rubric.criteria}
    max_scores = {c["name"]: c["max_points"] for c in rubric.criteria}

    for name, score in request.criteria_scores.items():
        if name not in criterion_names:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid criterion name: {name}"
            )
        if score < 0 or score > max_scores[name]:
            raise HTTPException(
                status_code=400,
                detail=f"Score for {name} must be between 0 and {max_scores[name]}"
            )

    updated_criteria = grade.criteria_scores.copy()
    for name, new_score in request.criteria_scores.items():
        if name in updated_criteria:
            updated_criteria[name]["score"] = new_score
        else:
            updated_criteria[name] = {
                "score": new_score,
                "max_score": max_scores[name],
                "evidence": "Instructor override",
                "feedback": "Score adjusted by instructor",
            }

    new_total = sum(c["score"] for c in updated_criteria.values())

    grade.criteria_scores = updated_criteria
    grade.total_score = new_total
    grade.instructor_override = True
    grade.override_reason = request.reason
    grade.graded_by = GradedBy.INSTRUCTOR
    grade.graded_at = datetime.utcnow()

    db.commit()
    db.refresh(grade)

    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()

    return _grade_to_response(grade, rubric, conversation)


@router.get("/rubrics/{rubric_id}", response_model=RubricResponse)
async def get_rubric(
    rubric_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get rubric details."""
    rubric = db.query(Rubric).filter(Rubric.id == rubric_id).first()

    if not rubric:
        raise HTTPException(status_code=404, detail="Rubric not found")

    return RubricResponse(
        id=rubric.id,
        name=rubric.name,
        criteria=rubric.criteria,
        total_points=rubric.total_points,
    )


@router.get("/needs-review", response_model=list[GradeSummary])
async def list_grades_needing_review(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = 20,
):
    """List grades that need instructor review (low confidence)."""
    if current_user.role.value not in ["instructor", "admin"]:
        raise HTTPException(
            status_code=403,
            detail="Only instructors can view grades needing review"
        )

    grades = (
        db.query(Grade)
        .filter(Grade.ai_confidence < 0.7)
        .filter(Grade.instructor_override == False)
        .order_by(Grade.graded_at.desc())
        .limit(limit)
        .all()
    )

    return [
        GradeSummary(
            id=g.id,
            conversation_id=g.conversation_id,
            total_score=float(g.total_score),
            graded_by=g.graded_by.value,
            graded_at=g.graded_at,
            needs_review=g.needs_review,
        )
        for g in grades
    ]
