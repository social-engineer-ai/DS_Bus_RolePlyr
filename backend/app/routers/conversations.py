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
    EndConversationRequest,
    ScenarioResponse,
    ViolationRequest,
    ViolationResponse,
)
from app.services.conversation_engine import ConversationEngine
from app.routers.auth import get_current_user

router = APIRouter()


@router.get("/scenarios", response_model=list[ScenarioResponse])
async def list_scenarios(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
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
    current_user: User = Depends(get_current_user),
):
    """Start a new conversation with a stakeholder persona."""
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
        user_id=current_user.id,
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
    engine = ConversationEngine(persona=persona, context=request.context, scenario_description=scenario.description)
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
    current_user: User = Depends(get_current_user),
):
    """Get conversation details and message history."""
    conversation = (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id)
        .first()
    )
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Check ownership (instructors/admins can view any conversation)
    if conversation.user_id != current_user.id and current_user.role.value not in ["instructor", "admin"]:
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
        violation_count=conversation.violation_count,
        violation_log=conversation.violation_log,
        ended_at=conversation.ended_at,
        total_active_seconds=conversation.total_active_seconds,
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
    current_user: User = Depends(get_current_user),
):
    """Send a message and get the stakeholder's response."""
    # Get conversation
    conversation = (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id)
        .first()
    )
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if conversation.user_id != current_user.id:
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
    request: EndConversationRequest = EndConversationRequest(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """End a conversation and trigger grading."""
    conversation = (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id)
        .first()
    )
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if conversation.user_id != current_user.id:
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
    now = datetime.utcnow()
    conversation.status = ConversationStatus.COMPLETED
    conversation.completed_at = now
    conversation.ended_at = now
    if request.total_active_seconds is not None:
        conversation.total_active_seconds = request.total_active_seconds

    db.commit()
    db.refresh(closing_message)

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


@router.post("/{conversation_id}/violations", response_model=ViolationResponse)
async def log_violation(
    conversation_id: UUID,
    request: ViolationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Log a screen lock violation for a conversation."""
    conversation = (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id)
        .first()
    )
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if conversation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Append to violation log
    log_entry = {
        "violation_number": request.violation_number,
        "timestamp": request.timestamp,
        "turn_number": request.turn_number,
    }
    if conversation.violation_log is None:
        conversation.violation_log = [log_entry]
    else:
        conversation.violation_log = conversation.violation_log + [log_entry]

    conversation.violation_count = len(conversation.violation_log)

    db.commit()
    db.refresh(conversation)

    return ViolationResponse(
        violation_count=conversation.violation_count,
        violation_log=conversation.violation_log,
    )


@router.get("", response_model=list[ConversationListItem])
async def list_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = 20,
    offset: int = 0,
):
    """List user's conversations."""
    conversations = (
        db.query(Conversation)
        .filter(Conversation.user_id == current_user.id)
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
