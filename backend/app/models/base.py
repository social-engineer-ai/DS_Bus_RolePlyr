"""Base model configuration."""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class TimestampMixin:
    """Mixin for created_at timestamp."""

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class UUIDMixin:
    """Mixin for UUID primary key."""

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
