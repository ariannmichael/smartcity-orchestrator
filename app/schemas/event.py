from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class IngestResponse(BaseModel):
    stored_event_id: UUID = Field(..., description="The ID of the stored event")
    derived_event_ids: list[UUID] = Field(..., description="The IDs of the derived events")


class EventOut(BaseModel):
    id: UUID = Field(..., description="The ID of the event")
    service: str = Field(..., description="The service that produced the event")
    timestamp: datetime = Field(..., description="The timestamp of the event")
    payload: dict = Field(..., description="The payload of the event")
    normalized_payload: dict | None = Field(None, description="The normalized payload of the event")
    source_event_id: UUID | None = Field(None, description="The ID of the source event")
    
    model_config = {"from_attributes": True}