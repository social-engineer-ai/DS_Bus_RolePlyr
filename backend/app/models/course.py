"""Course and Enrollment models."""

from sqlalchemy import Column, String, ForeignKey, Enum as SQLEnum, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from app.database import Base
from app.models.base import UUIDMixin, TimestampMixin


class EnrollmentRole(str, enum.Enum):
    """Roles within a course."""

    STUDENT = "student"
    TA = "ta"
    INSTRUCTOR = "instructor"


class Course(Base, UUIDMixin, TimestampMixin):
    """Course model."""

    __tablename__ = "courses"

    name = Column(String(255), nullable=False)
    instructor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Relationships
    instructor = relationship("User", back_populates="courses_taught")
    enrollments = relationship("Enrollment", back_populates="course")
    personas = relationship("Persona", back_populates="course")
    rubrics = relationship("Rubric", back_populates="course")
    scenarios = relationship("Scenario", back_populates="course")
    assignments = relationship("Assignment", back_populates="course")
    daily_analytics = relationship("DailyAnalytics", back_populates="course")

    def __repr__(self):
        return f"<Course {self.name}>"


class Enrollment(Base, UUIDMixin):
    """Course enrollment model."""

    __tablename__ = "enrollments"
    __table_args__ = (UniqueConstraint("user_id", "course_id", name="uq_user_course"),)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id"), nullable=False)
    role = Column(SQLEnum(EnrollmentRole), nullable=False, default=EnrollmentRole.STUDENT)

    # Relationships
    user = relationship("User", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")

    def __repr__(self):
        return f"<Enrollment user={self.user_id} course={self.course_id} role={self.role.value}>"
