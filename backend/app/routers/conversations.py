"""Conversation API endpoints."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.conversation import (
    Conversation,
    Message,
    MessageRole,
    ConversationMode,
    ConversationStatus,
)
from app.models.scenario import Scenario
from app.models.persona import Persona
from app.models.user import User
from app.schemas.conversation import (
    StartConversationRequest,
    SendMessageRequest,
    ConversationResponse,
    ConversationListItem,
    MessageResponse,
    StakeholderMessageResponse,
    EndConversationResponse,
    ScenarioResponse,
)
from app.services.conversation_engine import ConversationEngine
from app.routers.auth import get_current_user_from_token, MOCK_USERS

router = APIRouter()


# Temporary helper to get user from query param (will be middleware later)
def get_current_user_id(user_key: Optional[str] = None) -> UUID:
    """Get current user ID from mock auth.

    In production, this would come from OAuth token.
    """
    if not user_key:
        # Default to student1 for development
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


def is_instructor_or_admin(user_key: Optional[str] = None) -> bool:
    """Check if user is instructor or admin."""
    role = get_user_role(user_key)
    return role in ["instructor", "admin"]


@router.get("/scenarios", response_model=list[ScenarioResponse])
async def list_scenarios(
    db: Session = Depends(get_db),
    user_key: Optional[str] = None,
):
    """List available scenarios for practice."""
    scenarios = db.query(Scenario).filter(Scenario.is_practice == True).all()

    result = []
    for scenario in scenarios:
        persona = db.query(Persona).filter(Persona.id == scenario.persona_id).first()
        result.append(
            ScenarioResponse(
                id=scenario.id,
                name=scenario.name,
                description=scenario.description,
                persona_name=persona.name if persona else "Unknown",
                persona_title=persona.title if persona else "",
                persona_background=persona.background if persona else None,
                is_practice=scenario.is_practice,
                max_turns=scenario.max_turns,
            )
        )
    return result


@router.post("", response_model=ConversationResponse)
async def start_conversation(
    request: StartConversationRequest,
    db: Session = Depends(get_db),
    user_key: Optional[str] = None,
):
    """Start a new conversation with a stakeholder persona."""
    user_id = get_current_user_id(user_key)

    # Get scenario
    scenario = db.query(Scenario).filter(Scenario.id == request.scenario_id).first()
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    # Get persona
    persona = db.query(Persona).filter(Persona.id == scenario.persona_id).first()
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")

    # Determine mode
    mode = ConversationMode.GRADED if request.assignment_id else ConversationMode.PRACTICE

    # Create conversation
    conversation = Conversation(
        user_id=user_id,
        scenario_id=scenario.id,
        assignment_id=request.assignment_id,
        context=request.context,
        mode=mode,
        status=ConversationStatus.IN_PROGRESS,
        turn_count=0,
    )
    db.add(conversation)
    db.flush()

    # Generate opening message from stakeholder
    engine = ConversationEngine(persona=persona, context=request.context)
    opening_message = await engine.get_opening_message()

    # Save stakeholder's opening message
    message = Message(
        conversation_id=conversation.id,
        role=MessageRole.STAKEHOLDER,
        content=opening_message,
    )
    db.add(message)
    conversation.turn_count = 1

    db.commit()
    db.refresh(conversation)

    return ConversationResponse(
        id=conversation.id,
        scenario_id=conversation.scenario_id,
        persona_name=persona.name,
        persona_title=persona.title,
        mode=conversation.mode.value,
        status=conversation.status.value,
        context=conversation.context,
        turn_count=conversation.turn_count,
        started_at=conversation.started_at,
        messages=[
            MessageResponse(
                id=message.id,
                role=message.role.value,
                content=message.content,
                created_at=message.created_at,
            )
        ],
    )


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: UUID,
    db: Session = Depends(get_db),
    user_key: Optional[str] = None,
):
    """Get conversation details and message history."""
    user_id = get_current_user_id(user_key)

    conversation = (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id)
        .first()
    )
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Check ownership (instructors/admins can view any conversation)
    if conversation.user_id != user_id and not is_instructor_or_admin(user_key):
        raise HTTPException(status_code=403, detail="Not authorized")

    # Get persona
    scenario = db.query(Scenario).filter(Scenario.id == conversation.scenario_id).first()
    persona = db.query(Persona).filter(Persona.id == scenario.persona_id).first()

    # Get messages
    messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
        .all()
    )

    return ConversationResponse(
        id=conversation.id,
        scenario_id=conversation.scenario_id,
        persona_name=persona.name if persona else "Unknown",
        persona_title=persona.title if persona else "",
        mode=conversation.mode.value,
        status=conversation.status.value,
        context=conversation.context,
        turn_count=conversation.turn_count,
        started_at=conversation.started_at,
        completed_at=conversation.completed_at,
        messages=[
            MessageResponse(
                id=msg.id,
                role=msg.role.value,
                content=msg.content,
                created_at=msg.created_at,
            )
            for msg in messages
        ],
    )


@router.post("/{conversation_id}/messages", response_model=StakeholderMessageResponse)
async def send_message(
    conversation_id: UUID,
    request: SendMessageRequest,
    db: Session = Depends(get_db),
    user_key: Optional[str] = None,
):
    """Send a message and get the stakeholder's response."""
    user_id = get_current_user_id(user_key)

    # Get conversation
    conversation = (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id)
        .first()
    )
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if conversation.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    if conversation.status != ConversationStatus.IN_PROGRESS:
        raise HTTPException(
            status_code=400, detail="Conversation is not active"
        )

    # Get scenario and persona
    scenario = db.query(Scenario).filter(Scenario.id == conversation.scenario_id).first()
    persona = db.query(Persona).filter(Persona.id == scenario.persona_id).first()

    # Save student message
    student_message = Message(
        conversation_id=conversation.id,
        role=MessageRole.STUDENT,
        content=request.content,
    )
    db.add(student_message)
    db.flush()

    # Load conversation history and generate response
    existing_messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
        .all()
    )

    engine = ConversationEngine(persona=persona, context=conversation.context)
    engine.load_history(existing_messages[:-1])  # Exclude the message we just added

    # Generate stakeholder response
    stakeholder_response = await engine.get_response(request.content)

    # Save stakeholder message
    stakeholder_message = Message(
        conversation_id=conversation.id,
        role=MessageRole.STAKEHOLDER,
        content=stakeholder_response,
    )
    db.add(stakeholder_message)

    # Update turn count
    conversation.turn_count += 1

    # Check if should end
    should_end = engine.should_end_conversation(
        conversation.turn_count, scenario.max_turns
    )

    db.commit()
    db.refresh(student_message)
    db.refresh(stakeholder_message)

    return StakeholderMessageResponse(
        student_message=MessageResponse(
            id=student_message.id,
            role=student_message.role.value,
            content=student_message.content,
            created_at=student_message.created_at,
        ),
        stakeholder_message=MessageResponse(
            id=stakeholder_message.id,
            role=stakeholder_message.role.value,
            content=stakeholder_message.content,
            created_at=stakeholder_message.created_at,
        ),
        conversation_status=conversation.status.value,
        turn_count=conversation.turn_count,
        should_end=should_end,
    )


@router.post("/{conversation_id}/end", response_model=EndConversationResponse)
async def end_conversation(
    conversation_id: UUID,
    db: Session = Depends(get_db),
    user_key: Optional[str] = None,
):
    """End a conversation and trigger grading."""
    user_id = get_current_user_id(user_key)

    conversation = (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id)
        .first()
    )
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if conversation.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    if conversation.status != ConversationStatus.IN_PROGRESS:
        raise HTTPException(
            status_code=400, detail="Conversation is not active"
        )

    # Get scenario and persona for closing message
    scenario = db.query(Scenario).filter(Scenario.id == conversation.scenario_id).first()
    persona = db.query(Persona).filter(Persona.id == scenario.persona_id).first()

    # Generate closing message
    existing_messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
        .all()
    )

    engine = ConversationEngine(persona=persona, context=conversation.context)
    engine.load_history(existing_messages)

    closing_message_text = await engine.get_closing_message()

    # Save closing message
    closing_message = Message(
        conversation_id=conversation.id,
        role=MessageRole.STAKEHOLDER,
        content=closing_message_text,
    )
    db.add(closing_message)

    # Update conversation status
    conversation.status = ConversationStatus.COMPLETED
    conversation.completed_at = datetime.utcnow()

    db.commit()
    db.refresh(closing_message)

    # TODO: Trigger grading in background

    return EndConversationResponse(
        id=conversation.id,
        status=conversation.status.value,
        turn_count=conversation.turn_count,
        completed_at=conversation.completed_at,
        final_message=MessageResponse(
            id=closing_message.id,
            role=closing_message.role.value,
            content=closing_message.content,
            created_at=closing_message.created_at,
        ),
    )


@router.get("", response_model=list[ConversationListItem])
async def list_conversations(
    db: Session = Depends(get_db),
    user_key: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
):
    """List user's conversations."""
    user_id = get_current_user_id(user_key)

    conversations = (
        db.query(Conversation)
        .filter(Conversation.user_id == user_id)
        .order_by(Conversation.started_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    result = []
    for conv in conversations:
        scenario = db.query(Scenario).filter(Scenario.id == conv.scenario_id).first()
        persona = db.query(Persona).filter(Persona.id == scenario.persona_id).first() if scenario else None

        # Get score if graded
        score = None
        if conv.grade:
            score = float(conv.grade.total_score)

        result.append(
            ConversationListItem(
                id=conv.id,
                scenario_id=conv.scenario_id,
                persona_name=persona.name if persona else "Unknown",
                mode=conv.mode.value,
                status=conv.status.value,
                turn_count=conv.turn_count,
                started_at=conv.started_at,
                completed_at=conv.completed_at,
                score=score,
            )
        )

    return result
