"""Rubric model for grading criteria."""

from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.base import UUIDMixin, TimestampMixin


class Rubric(Base, UUIDMixin, TimestampMixin):
    """Grading rubric model.

    Criteria format:
    [
        {
            "name": "business_value_articulation",
            "display_name": "Business Value Articulation",
            "description": "...",
            "max_points": 25,
            "scoring_guide": {
                "25": "Clearly quantified business impact with specific numbers",
                "20": "Described business value but lacked specific metrics",
                ...
            }
        },
        ...
    ]
    """

    __tablename__ = "rubrics"

    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id"), nullable=True)
    name = Column(String(255), nullable=False)
    criteria = Column(JSONB, nullable=False)  # Array of criterion objects

    # Relationships
    course = relationship("Course", back_populates="rubrics")
    scenarios = relationship("Scenario", back_populates="rubric")
    grades = relationship("Grade", back_populates="rubric")

    def __repr__(self):
        return f"<Rubric {self.name}>"

    @property
    def total_points(self) -> int:
        """Calculate total possible points."""
        if not self.criteria:
            return 0
        return sum(c.get("max_points", 0) for c in self.criteria)

    def to_prompt_text(self) -> str:
        """Convert rubric to text format for LLM prompts."""
        lines = [f"GRADING RUBRIC: {self.name}", "=" * 40, ""]

        for criterion in self.criteria or []:
            lines.append(f"{criterion['display_name']} ({criterion['max_points']} points)")
            lines.append(f"  {criterion.get('description', '')}")
            if "scoring_guide" in criterion:
                for score, desc in criterion["scoring_guide"].items():
                    lines.append(f"    {score}: {desc}")
            lines.append("")

        return "\n".join(lines)
