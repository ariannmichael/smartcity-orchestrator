from datetime import datetime
from uuid import UUID
from typing import List
from pydantic import BaseModel, ConfigDict, Field


class IngestResponse(BaseModel):
    stored_event_id: UUID = Field(..., description="The ID of the stored event")
    derived_events: List[UUID] = Field(..., description="The IDs of the derived events")


class EventOut(BaseModel):
    id: UUID = Field(..., description="The ID of the event")
    service: str = Field(..., description="The service that produced the event")
    timestamp: datetime = Field(..., description="The timestamp of the event")
    payload: dict = Field(..., description="The payload of the event")
    normalized_payload: dict | None = Field(None, description="The normalized payload of the event (optional)")
    deduplication_key: str | None = Field(None, description="The deduplication key of the event (optional)")
    source_event_id: UUID | None = Field(None, description="The ID of the source event (optional)")
    created_at: datetime = Field(..., description="The timestamp of the event creation")

    model_config = ConfigDict(from_attributes=True)