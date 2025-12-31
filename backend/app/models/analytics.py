"""Daily analytics model for course performance tracking."""

from sqlalchemy import Column, Integer, Date, ForeignKey, UniqueConstraint, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.base import UUIDMixin


class DailyAnalytics(Base, UUIDMixin):
    """Aggregated daily analytics for a course."""

    __tablename__ = "daily_analytics"
    __table_args__ = (UniqueConstraint("course_id", "date", name="uq_course_date"),)

    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id"), nullable=False)
    date = Column(Date, nullable=False)
    total_conversations = Column(Integer, default=0, nullable=False)
    total_practice = Column(Integer, default=0, nullable=False)
    total_graded = Column(Integer, default=0, nullable=False)
    avg_score = Column(Numeric(5, 2), nullable=True)
    common_struggles = Column(JSONB, nullable=True)  # AI-identified patterns

    # Relationships
    course = relationship("Course", back_populates="daily_analytics")

    def __repr__(self):
        return f"<DailyAnalytics {self.course_id} {self.date}>"
