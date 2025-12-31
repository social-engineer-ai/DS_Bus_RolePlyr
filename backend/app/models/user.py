"""User model."""

from sqlalchemy import Column, String, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum

from app.database import Base
from app.models.base import UUIDMixin, TimestampMixin


class UserRole(str, enum.Enum):
    """User roles in the system."""

    STUDENT = "student"
    INSTRUCTOR = "instructor"
    ADMIN = "admin"


class User(Base, UUIDMixin, TimestampMixin):
    """User account model."""

    __tablename__ = "users"

    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.STUDENT)

    # Relationships
    enrollments = relationship("Enrollment", back_populates="user")
    conversations = relationship("Conversation", back_populates="user")
    courses_taught = relationship("Course", back_populates="instructor")

    def __repr__(self):
        return f"<User {self.email} ({self.role.value})>"
