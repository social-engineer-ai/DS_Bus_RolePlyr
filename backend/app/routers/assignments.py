"""Assignment API endpoints."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.assignment import Assignment
from app.models.scenario import Scenario
from app.models.persona import Persona
from app.models.conversation import Conversation, ConversationStatus
from app.models.user import User
from app.schemas.assignment import (
    AssignmentCreate,
    AssignmentUpdate,
    AssignmentResponse,
    AssignmentListItem,
    StudentAssignment,
    AssignmentSubmission,
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


def require_instructor(user_key: Optional[str] = None):
    """Require instructor or admin role."""
    role = get_user_role(user_key)
    if role not in ["instructor", "admin"]:
        raise HTTPException(status_code=403, detail="Instructor access required")


@router.post("", response_model=AssignmentResponse)
async def create_assignment(
    assignment_data: AssignmentCreate,
    db: Session = Depends(get_db),
    user_key: Optional[str] = None,
):
    """Create a new assignment (instructor only)."""
    require_instructor(user_key)

    # Verify scenario exists
    scenario = db.query(Scenario).filter(Scenario.id == assignment_data.scenario_id).first()
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    # Create assignment
    assignment = Assignment(
        course_id=assignment_data.course_id,
        scenario_id=assignment_data.scenario_id,
        title=assignment_data.title,
        instructions=assignment_data.instructions,
        due_date=assignment_data.due_date,
        max_attempts=assignment_data.max_attempts,
        is_active=assignment_data.is_active,
    )

    db.add(assignment)
    db.commit()
    db.refresh(assignment)

    # Get persona info
    persona = db.query(Persona).filter(Persona.id == scenario.persona_id).first()

    return AssignmentResponse(
        id=assignment.id,
        title=assignment.title,
        instructions=assignment.instructions,
        due_date=assignment.due_date,
        max_attempts=assignment.max_attempts,
        is_active=assignment.is_active,
        scenario_id=assignment.scenario_id,
        course_id=assignment.course_id,
        scenario_name=scenario.name,
        persona_name=persona.name if persona else "Unknown",
        created_at=assignment.created_at,
        updated_at=assignment.updated_at,
    )


@router.get("", response_model=List[AssignmentListItem])
async def list_assignments(
    course_id: Optional[UUID] = None,
    active_only: bool = False,
    db: Session = Depends(get_db),
    user_key: Optional[str] = None,
):
    """List all assignments (instructor view)."""
    require_instructor(user_key)

    query = db.query(Assignment)
    if course_id:
        query = query.filter(Assignment.course_id == course_id)
    if active_only:
        query = query.filter(Assignment.is_active == True)

    assignments = query.order_by(desc(Assignment.created_at)).all()

    result = []
    for assignment in assignments:
        scenario = db.query(Scenario).filter(Scenario.id == assignment.scenario_id).first()
        persona = db.query(Persona).filter(Persona.id == scenario.persona_id).first() if scenario else None

        # Count submissions
        submissions = db.query(Conversation).filter(
            Conversation.assignment_id == assignment.id
        ).all()
        graded = len([s for s in submissions if s.grade is not None])

        result.append(AssignmentListItem(
            id=assignment.id,
            title=assignment.title,
            scenario_name=scenario.name if scenario else "Unknown",
            persona_name=persona.name if persona else "Unknown",
            due_date=assignment.due_date,
            max_attempts=assignment.max_attempts,
            is_active=assignment.is_active,
            total_submissions=len(submissions),
            graded_submissions=graded,
        ))

    return result


@router.get("/student", response_model=List[StudentAssignment])
async def get_student_assignments(
    db: Session = Depends(get_db),
    user_key: Optional[str] = None,
):
    """Get assignments available to current student."""
    user_id = get_current_user_id(user_key)

    # Get all active assignments
    assignments = db.query(Assignment).filter(Assignment.is_active == True).all()

    result = []
    for assignment in assignments:
        scenario = db.query(Scenario).filter(Scenario.id == assignment.scenario_id).first()
        if not scenario:
            continue

        persona = db.query(Persona).filter(Persona.id == scenario.persona_id).first()
        if not persona:
            continue

        # Count student's attempts
        attempts = db.query(Conversation).filter(
            Conversation.assignment_id == assignment.id,
            Conversation.user_id == user_id,
        ).all()

        attempts_used = len(attempts)
        best_score = None
        for attempt in attempts:
            if attempt.grade:
                score = float(attempt.grade.total_score)
                if best_score is None or score > best_score:
                    best_score = score

        # Check if can attempt
        can_attempt = attempts_used < assignment.max_attempts
        if assignment.due_date and datetime.utcnow() > assignment.due_date:
            can_attempt = False

        result.append(StudentAssignment(
            id=assignment.id,
            title=assignment.title,
            instructions=assignment.instructions,
            scenario_name=scenario.name,
            persona_name=persona.name,
            persona_title=persona.title,
            due_date=assignment.due_date,
            max_attempts=assignment.max_attempts,
            attempts_used=attempts_used,
            best_score=best_score,
            can_attempt=can_attempt,
        ))

    return result


@router.get("/{assignment_id}", response_model=AssignmentResponse)
async def get_assignment(
    assignment_id: UUID,
    db: Session = Depends(get_db),
    user_key: Optional[str] = None,
):
    """Get assignment details."""
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    scenario = db.query(Scenario).filter(Scenario.id == assignment.scenario_id).first()
    persona = db.query(Persona).filter(Persona.id == scenario.persona_id).first() if scenario else None

    return AssignmentResponse(
        id=assignment.id,
        title=assignment.title,
        instructions=assignment.instructions,
        due_date=assignment.due_date,
        max_attempts=assignment.max_attempts,
        is_active=assignment.is_active,
        scenario_id=assignment.scenario_id,
        course_id=assignment.course_id,
        scenario_name=scenario.name if scenario else "Unknown",
        persona_name=persona.name if persona else "Unknown",
        created_at=assignment.created_at,
        updated_at=assignment.updated_at,
    )


@router.put("/{assignment_id}", response_model=AssignmentResponse)
async def update_assignment(
    assignment_id: UUID,
    update_data: AssignmentUpdate,
    db: Session = Depends(get_db),
    user_key: Optional[str] = None,
):
    """Update an assignment (instructor only)."""
    require_instructor(user_key)

    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    # Update fields if provided
    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(assignment, key, value)

    db.commit()
    db.refresh(assignment)

    scenario = db.query(Scenario).filter(Scenario.id == assignment.scenario_id).first()
    persona = db.query(Persona).filter(Persona.id == scenario.persona_id).first() if scenario else None

    return AssignmentResponse(
        id=assignment.id,
        title=assignment.title,
        instructions=assignment.instructions,
        due_date=assignment.due_date,
        max_attempts=assignment.max_attempts,
        is_active=assignment.is_active,
        scenario_id=assignment.scenario_id,
        course_id=assignment.course_id,
        scenario_name=scenario.name if scenario else "Unknown",
        persona_name=persona.name if persona else "Unknown",
        created_at=assignment.created_at,
        updated_at=assignment.updated_at,
    )


@router.delete("/{assignment_id}")
async def delete_assignment(
    assignment_id: UUID,
    db: Session = Depends(get_db),
    user_key: Optional[str] = None,
):
    """Delete an assignment (instructor only). Sets inactive instead of hard delete."""
    require_instructor(user_key)

    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    # Soft delete - set inactive
    assignment.is_active = False
    db.commit()

    return {"message": "Assignment deactivated"}


@router.get("/{assignment_id}/submissions", response_model=List[AssignmentSubmission])
async def get_assignment_submissions(
    assignment_id: UUID,
    db: Session = Depends(get_db),
    user_key: Optional[str] = None,
):
    """Get all submissions for an assignment (instructor only)."""
    require_instructor(user_key)

    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    conversations = db.query(Conversation).filter(
        Conversation.assignment_id == assignment_id
    ).order_by(desc(Conversation.started_at)).all()

    result = []
    for conv in conversations:
        student = db.query(User).filter(User.id == conv.user_id).first()
        result.append(AssignmentSubmission(
            id=conv.id,
            conversation_id=conv.id,
            student_id=conv.user_id,
            student_name=student.name if student else "Unknown",
            started_at=conv.started_at,
            completed_at=conv.completed_at,
            score=float(conv.grade.total_score) if conv.grade else None,
            status=conv.status.value,
        ))

    return result
