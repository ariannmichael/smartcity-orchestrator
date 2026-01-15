import uuid
from datetime import datetime

from sqlalchemy import DateTime, Text, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class Event(Base):
    __tablename__ = "events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    service: Mapped[str] = mapped_column(Text, index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())

    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    normalized_payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    source_event_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), index=True)
    deduplication_key: Mapped[str | None] = mapped_column(Text, index=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())
