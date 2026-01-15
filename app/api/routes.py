from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.application.ingest import ingest_event
from app.core.db import get_db
from app.api.schemas import EventOut, IngestResponse
from app.infra.persistence.models.event import Event


router = APIRouter()

@router.get("/health")
def health_check():
    return {"status": "ok"}


@router.post("/ingest/{service}", response_model=IngestResponse)
def ingest(
    service: str,
    payload: dict,
    db: Session = Depends(get_db),
    dedupe_key: str | None = None,
) -> IngestResponse:
    try:
        base, derived_events = ingest_event(service, payload, db, dedupe_key)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return IngestResponse(
        stored_event_id=base.id,
        derived_events=[event.id for event in derived_events],
    )


@router.get("/events", response_model=List[EventOut])
def get_events(
    db: Session = Depends(get_db),
    limit: int = 100,
    offset: int = 0,
) -> List[EventOut]:
    if limit > 100:
        raise HTTPException(status_code=400, detail="Limit must be less than or equal to 100")

    events = db.execute(select(Event).order_by(Event.created_at.desc()).limit(limit).offset(offset)).scalars().all()
    return [EventOut.model_validate(event) for event in events]