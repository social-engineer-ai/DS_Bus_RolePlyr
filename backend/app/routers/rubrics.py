"""Rubric API endpoints, including AI rubric builder."""

import json
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.rubric import Rubric
from app.models.scenario import Scenario
from app.models.user import User
from app.schemas.rubric import (
    RubricCreate,
    RubricUpdate,
    RubricResponse,
    RubricListItem,
    RubricChatRequest,
    RubricChatResponse,
    MaterialUploadResponse,
)
from app.routers.auth import get_current_user
from app.services.llm_client import get_llm_client

router = APIRouter()

MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB


def _require_instructor(current_user: User):
    if current_user.role.value not in ["instructor", "admin"]:
        raise HTTPException(status_code=403, detail="Instructor access required")


@router.post("", response_model=RubricResponse)
async def create_rubric(
    rubric_data: RubricCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new rubric (instructor only)."""
    _require_instructor(current_user)

    criteria_dicts = [c.model_dump() for c in rubric_data.criteria]

    rubric = Rubric(
        course_id=rubric_data.course_id,
        name=rubric_data.name,
        criteria=criteria_dicts,
    )

    db.add(rubric)
    db.commit()
    db.refresh(rubric)

    return RubricResponse(
        id=rubric.id,
        course_id=rubric.course_id,
        name=rubric.name,
        criteria=rubric.criteria,
        total_points=rubric.total_points,
        created_at=rubric.created_at,
    )


@router.get("", response_model=List[RubricListItem])
async def list_rubrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all rubrics (instructor view)."""
    _require_instructor(current_user)

    rubrics = db.query(Rubric).order_by(desc(Rubric.created_at)).all()

    return [
        RubricListItem(
            id=r.id,
            name=r.name,
            total_points=r.total_points,
            criteria_count=len(r.criteria) if r.criteria else 0,
            created_at=r.created_at,
        )
        for r in rubrics
    ]


@router.get("/{rubric_id}", response_model=RubricResponse)
async def get_rubric(
    rubric_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get rubric details with computed total_points."""
    rubric = db.query(Rubric).filter(Rubric.id == rubric_id).first()
    if not rubric:
        raise HTTPException(status_code=404, detail="Rubric not found")

    return RubricResponse(
        id=rubric.id,
        course_id=rubric.course_id,
        name=rubric.name,
        criteria=rubric.criteria,
        total_points=rubric.total_points,
        created_at=rubric.created_at,
    )


@router.put("/{rubric_id}", response_model=RubricResponse)
async def update_rubric(
    rubric_id: UUID,
    update_data: RubricUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a rubric (instructor only)."""
    _require_instructor(current_user)

    rubric = db.query(Rubric).filter(Rubric.id == rubric_id).first()
    if not rubric:
        raise HTTPException(status_code=404, detail="Rubric not found")

    update_dict = update_data.model_dump(exclude_unset=True)
    if "criteria" in update_dict and update_dict["criteria"] is not None:
        update_dict["criteria"] = [
            c.model_dump() if hasattr(c, "model_dump") else c
            for c in update_data.criteria
        ]

    for key, value in update_dict.items():
        setattr(rubric, key, value)

    db.commit()
    db.refresh(rubric)

    return RubricResponse(
        id=rubric.id,
        course_id=rubric.course_id,
        name=rubric.name,
        criteria=rubric.criteria,
        total_points=rubric.total_points,
        created_at=rubric.created_at,
    )


@router.delete("/{rubric_id}")
async def delete_rubric(
    rubric_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a rubric (instructor only). Blocks if referenced by scenarios."""
    _require_instructor(current_user)

    rubric = db.query(Rubric).filter(Rubric.id == rubric_id).first()
    if not rubric:
        raise HTTPException(status_code=404, detail="Rubric not found")

    referencing_scenarios = db.query(Scenario).filter(Scenario.rubric_id == rubric_id).count()
    if referencing_scenarios > 0:
        raise HTTPException(
            status_code=409,
            detail=f"Cannot delete rubric: {referencing_scenarios} scenario(s) reference it",
        )

    db.delete(rubric)
    db.commit()

    return {"message": "Rubric deleted"}


# --- AI Rubric Builder endpoints ---


@router.post("/upload-material", response_model=MaterialUploadResponse)
async def upload_material(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """Upload a PDF or DOCX file and extract text for the rubric builder."""
    _require_instructor(current_user)

    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ("pdf", "docx"):
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported")

    content = await file.read()
    if len(content) > MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=400, detail="File too large (max 10MB)")

    extracted_text = ""
    pages = None

    if ext == "pdf":
        try:
            from PyPDF2 import PdfReader
            import io

            reader = PdfReader(io.BytesIO(content))
            pages = len(reader.pages)
            text_parts = []
            for page in reader.pages:
                text_parts.append(page.extract_text() or "")
            extracted_text = "\n\n".join(text_parts)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to read PDF: {str(e)}")

    elif ext == "docx":
        try:
            from docx import Document
            import io

            doc = Document(io.BytesIO(content))
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            extracted_text = "\n\n".join(paragraphs)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to read DOCX: {str(e)}")

    if not extracted_text.strip():
        raise HTTPException(status_code=400, detail="No text could be extracted from the file")

    return MaterialUploadResponse(
        extracted_text=extracted_text,
        filename=file.filename,
        pages=pages,
    )


RUBRIC_BUILDER_SYSTEM_PROMPT = """You are a rubric design assistant for an educational stakeholder communication simulation platform called StakeholderSim.

Your job is to help instructors create grading rubrics for role-play scenarios where students practice communicating with stakeholders (executives, project managers, clients, etc.).

When the instructor provides materials (syllabus excerpts, learning objectives, assignment descriptions), analyze them and propose a rubric with clear criteria.

IMPORTANT: You must ALWAYS respond with valid JSON in this exact format:
{
  "reply": "Your conversational response to the instructor",
  "rubric_draft": {
    "name": "Rubric Name",
    "criteria": [
      {
        "name": "criterion_snake_case",
        "display_name": "Criterion Display Name",
        "description": "What this criterion measures",
        "max_points": 25,
        "scoring_guide": {
          "25": "Excellent - description",
          "20": "Good - description",
          "15": "Adequate - description",
          "10": "Below expectations - description",
          "5": "Minimal - description"
        }
      }
    ]
  }
}

If the instructor hasn't provided enough information to create a rubric yet, set rubric_draft to null and ask clarifying questions in the reply.

Guidelines for rubric design:
- Total points should sum to 100
- 3-6 criteria is typical
- Each criterion needs a clear scoring guide with at least 3 levels
- Criteria should be measurable and specific to stakeholder communication skills
- Common criteria areas: communication clarity, stakeholder empathy, business value articulation, objection handling, technical translation, professionalism"""


@router.post("/chat", response_model=RubricChatResponse)
async def rubric_chat(
    request: RubricChatRequest,
    current_user: User = Depends(get_current_user),
):
    """Chat with AI to build a rubric. Stateless — full message history sent each time."""
    _require_instructor(current_user)

    llm = get_llm_client()

    system_prompt = RUBRIC_BUILDER_SYSTEM_PROMPT
    if request.materials_text:
        system_prompt += f"\n\nThe instructor has provided the following materials:\n\n{request.materials_text}"

    messages = [
        {"role": msg.role, "content": msg.content}
        for msg in request.messages
    ]

    try:
        raw_response = await llm.generate_json_response(
            system_prompt=system_prompt,
            messages=messages,
            max_tokens=3000,
        )

        # Parse the JSON response
        # Strip markdown code fences if present
        cleaned = raw_response.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            # Remove first line (```json) and last line (```)
            lines = [l for l in lines if not l.strip().startswith("```")]
            cleaned = "\n".join(lines)

        parsed = json.loads(cleaned)

        return RubricChatResponse(
            reply=parsed.get("reply", ""),
            rubric_draft=parsed.get("rubric_draft"),
        )
    except json.JSONDecodeError:
        # If JSON parsing fails, return the raw text as the reply
        return RubricChatResponse(
            reply=raw_response,
            rubric_draft=None,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")
