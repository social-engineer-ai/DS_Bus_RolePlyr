"""Scenario API endpoints."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.assignment import Assignment
from app.models.persona import Persona
from app.models.rubric import Rubric
from app.models.scenario import Scenario
from app.models.user import User
from app.schemas.scenario import (
    ScenarioCreate,
    ScenarioUpdate,
    ScenarioResponse,
    ScenarioListItem,
)
from app.routers.auth import get_current_user

router = APIRouter()


def _require_instructor(current_user: User):
    if current_user.role.value not in ["instructor", "admin"]:
        raise HTTPException(status_code=403, detail="Instructor access required")


def _build_scenario_response(scenario: Scenario, persona: Persona, rubric: Rubric) -> ScenarioResponse:
    return ScenarioResponse(
        id=scenario.id,
        course_id=scenario.course_id,
        name=scenario.name,
        description=scenario.description,
        persona_id=scenario.persona_id,
        rubric_id=scenario.rubric_id,
        persona_name=persona.name if persona else "Unknown",
        rubric_name=rubric.name if rubric else "Unknown",
        is_practice=scenario.is_practice,
        max_turns=scenario.max_turns,
        created_at=scenario.created_at,
    )


@router.post("", response_model=ScenarioResponse)
async def create_scenario(
    scenario_data: ScenarioCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new scenario (instructor only). Validates persona_id and rubric_id exist."""
    _require_instructor(current_user)

    persona = db.query(Persona).filter(Persona.id == scenario_data.persona_id).first()
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")

    rubric = db.query(Rubric).filter(Rubric.id == scenario_data.rubric_id).first()
    if not rubric:
        raise HTTPException(status_code=404, detail="Rubric not found")

    scenario = Scenario(
        course_id=scenario_data.course_id,
        name=scenario_data.name,
        description=scenario_data.description,
        persona_id=scenario_data.persona_id,
        rubric_id=scenario_data.rubric_id,
        is_practice=scenario_data.is_practice,
        max_turns=scenario_data.max_turns,
    )

    db.add(scenario)
    db.commit()
    db.refresh(scenario)

    return _build_scenario_response(scenario, persona, rubric)


@router.get("", response_model=List[ScenarioListItem])
async def list_scenarios(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List ALL scenarios (not just practice)."""
    _require_instructor(current_user)

    scenarios = db.query(Scenario).order_by(desc(Scenario.created_at)).all()

    result = []
    for s in scenarios:
        persona = db.query(Persona).filter(Persona.id == s.persona_id).first()
        rubric = db.query(Rubric).filter(Rubric.id == s.rubric_id).first()
        result.append(ScenarioListItem(
            id=s.id,
            name=s.name,
            persona_name=persona.name if persona else "Unknown",
            rubric_name=rubric.name if rubric else "Unknown",
            is_practice=s.is_practice,
            max_turns=s.max_turns,
            created_at=s.created_at,
        ))

    return result


@router.get("/{scenario_id}", response_model=ScenarioResponse)
async def get_scenario(
    scenario_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get scenario details with persona_name and rubric_name."""
    scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    persona = db.query(Persona).filter(Persona.id == scenario.persona_id).first()
    rubric = db.query(Rubric).filter(Rubric.id == scenario.rubric_id).first()

    return _build_scenario_response(scenario, persona, rubric)


@router.put("/{scenario_id}", response_model=ScenarioResponse)
async def update_scenario(
    scenario_id: UUID,
    update_data: ScenarioUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a scenario (instructor only)."""
    _require_instructor(current_user)

    scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    update_dict = update_data.model_dump(exclude_unset=True)

    # Validate foreign keys if being updated
    if "persona_id" in update_dict:
        persona = db.query(Persona).filter(Persona.id == update_dict["persona_id"]).first()
        if not persona:
            raise HTTPException(status_code=404, detail="Persona not found")
    if "rubric_id" in update_dict:
        rubric = db.query(Rubric).filter(Rubric.id == update_dict["rubric_id"]).first()
        if not rubric:
            raise HTTPException(status_code=404, detail="Rubric not found")

    for key, value in update_dict.items():
        setattr(scenario, key, value)

    db.commit()
    db.refresh(scenario)

    persona = db.query(Persona).filter(Persona.id == scenario.persona_id).first()
    rubric = db.query(Rubric).filter(Rubric.id == scenario.rubric_id).first()

    return _build_scenario_response(scenario, persona, rubric)


@router.delete("/{scenario_id}")
async def delete_scenario(
    scenario_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a scenario (instructor only). Blocks if assignments reference it."""
    _require_instructor(current_user)

    scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    referencing_assignments = db.query(Assignment).filter(Assignment.scenario_id == scenario_id).count()
    if referencing_assignments > 0:
        raise HTTPException(
            status_code=409,
            detail=f"Cannot delete scenario: {referencing_assignments} assignment(s) reference it",
        )

    db.delete(scenario)
    db.commit()

    return {"message": "Scenario deleted"}
