"""Persona API endpoints."""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.persona import Persona
from app.models.user import User
from app.schemas.persona import (
    PersonaCreate,
    PersonaUpdate,
    PersonaResponse,
    PersonaListItem,
)
from app.routers.auth import get_current_user

router = APIRouter()


def _require_instructor(current_user: User):
    if current_user.role.value not in ["instructor", "admin"]:
        raise HTTPException(status_code=403, detail="Instructor access required")


@router.post("", response_model=PersonaResponse)
async def create_persona(
    persona_data: PersonaCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new persona (instructor only)."""
    _require_instructor(current_user)

    persona = Persona(
        course_id=persona_data.course_id,
        name=persona_data.name,
        title=persona_data.title,
        background=persona_data.background,
        personality=persona_data.personality,
        concerns=persona_data.concerns,
        required_questions=persona_data.required_questions,
    )

    db.add(persona)
    db.commit()
    db.refresh(persona)

    return PersonaResponse(
        id=persona.id,
        course_id=persona.course_id,
        name=persona.name,
        title=persona.title,
        background=persona.background,
        personality=persona.personality,
        concerns=persona.concerns,
        required_questions=persona.required_questions,
        is_active=persona.is_active,
        created_at=persona.created_at,
    )


@router.get("", response_model=List[PersonaListItem])
async def list_personas(
    course_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all personas (instructor view)."""
    _require_instructor(current_user)

    query = db.query(Persona).filter(Persona.is_active == True)
    if course_id:
        query = query.filter(Persona.course_id == course_id)

    personas = query.order_by(desc(Persona.created_at)).all()

    return [
        PersonaListItem(
            id=p.id,
            name=p.name,
            title=p.title,
            is_active=p.is_active,
            created_at=p.created_at,
        )
        for p in personas
    ]


@router.get("/{persona_id}", response_model=PersonaResponse)
async def get_persona(
    persona_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get persona details."""
    persona = db.query(Persona).filter(Persona.id == persona_id).first()
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")

    return PersonaResponse(
        id=persona.id,
        course_id=persona.course_id,
        name=persona.name,
        title=persona.title,
        background=persona.background,
        personality=persona.personality,
        concerns=persona.concerns,
        required_questions=persona.required_questions,
        is_active=persona.is_active,
        created_at=persona.created_at,
    )


@router.put("/{persona_id}", response_model=PersonaResponse)
async def update_persona(
    persona_id: UUID,
    update_data: PersonaUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a persona (instructor only)."""
    _require_instructor(current_user)

    persona = db.query(Persona).filter(Persona.id == persona_id).first()
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")

    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(persona, key, value)

    db.commit()
    db.refresh(persona)

    return PersonaResponse(
        id=persona.id,
        course_id=persona.course_id,
        name=persona.name,
        title=persona.title,
        background=persona.background,
        personality=persona.personality,
        concerns=persona.concerns,
        required_questions=persona.required_questions,
        is_active=persona.is_active,
        created_at=persona.created_at,
    )


@router.delete("/{persona_id}")
async def delete_persona(
    persona_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Soft-delete a persona (instructor only). Sets is_active=False."""
    _require_instructor(current_user)

    persona = db.query(Persona).filter(Persona.id == persona_id).first()
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")

    persona.is_active = False
    db.commit()

    return {"message": "Persona deactivated"}
