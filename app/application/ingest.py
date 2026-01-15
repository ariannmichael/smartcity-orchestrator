from __future__ import annotations

from typing import List, Tuple
import uuid

from sqlalchemy.orm import Session

from app.domain.events.types import NormalizedEvent
from app.domain.orchestration.factories.base import EventComponentsFactory
from app.domain.orchestration.registry import registry
from app.infra.outbox.enqueue import enqueue_notification
from app.infra.persistence.models.event import Event


def ingest_event(
    service: str,
    payload: dict,
    db: Session,
    dedupe_key: str | None = None,
) -> Tuple[Event, List[Event]]:
    if dedupe_key:
        existing = db.execute(select(Event).where(Event.deduplication_key == dedupe_key)).scalar_one_or_none()
        if existing:
            derived = db.execute(select(Event).where(Event.source_event_id == existing.id)).scalars().all()
            return existing, derived
    
    factory = registry.get(service)
    normalized = factory.normalizer().normalize(payload)

    base = Event(
        service=normalized.service,
        timestamp=normalized.timestamp,
        payload=normalized.raw_payload,
        normalized_payload=normalized.normalized_payload,
        source_event_id=None,
        deduplication_key=dedupe_key,
    )
    db.add(base)
    db.flush()

    derived_events = _persist_derived_events(normalized, factory, base.id, db)

    db.commit()
    db.refresh(base)
    for derived in derived_events:
        db.refresh(derived)

    return base, derived_events


def _persist_derived_events(normalized: NormalizedEvent, factory: EventComponentsFactory, base_id: uuid.UUID | None, db: Session) -> List[Event]:
    derived_specs = factory.rule_evaluator().evaluate(normalized)
    derived_events = []
    for spec in derived_specs:
        derived = Event(
            service=spec.service,
            payload=spec.payload,
            normalized_payload=None,
            source_event_id=base_id,
            deduplication_key=spec.deduplication_key if spec.deduplication_key else None,
        )
        db.add(derived)
        db.flush()
        derived_events.append(derived)

        enqueue_notification(db, spec.service, spec.payload)

    return derived_events