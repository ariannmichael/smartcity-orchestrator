from __future__ import annotations

from typing import Iterable, List, Tuple

from sqlalchemy.orm import Session

from app.domain.orchestration.registry import get_factory
from app.infra.persistence.models.event import Event
from app.infra.persistence.repositories.event_repo import EventRepository


def ingest_event(
    service: str,
    payload: dict,
    db: Session,
) -> Tuple[Event, List[Event]]:
    factory = get_factory(service)
    normalizer = factory.normalizer()
    evaluator = factory.rule_evaluator()

    normalized_event = normalizer.normalize(payload)

    event_repo = EventRepository(db)
    stored_event = event_repo.add(
        Event(
            service=normalized_event.service,
            payload=normalized_event.raw_payload,
            normalized_payload=normalized_event.normalized_payload,
        )
    )

    derived_specs = evaluator.evaluate(normalized_event)
    derived_events = _persist_derived_events(derived_specs, stored_event.id, event_repo)

    return stored_event, derived_events


def _persist_derived_events(
    derived_specs: Iterable,
    source_event_id,
    event_repo: EventRepository,
) -> List[Event]:
    derived_events: List[Event] = []
    for spec in derived_specs:
        derived_events.append(
            event_repo.add(
                Event(
                    service=spec.service,
                    payload=spec.payload,
                    normalized_payload=None,
                    source_event_id=source_event_id,
                    deduplication_key=spec.deduplication_key,
                )
            )
        )
    return derived_events
