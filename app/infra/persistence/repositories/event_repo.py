from __future__ import annotations

from sqlalchemy.orm import Session

from app.infra.persistence.models.event import Event


class EventRepository:
    def __init__(self, db: Session):
        self._db = db

    def add(self, event: Event) -> Event:
        self._db.add(event)
        self._db.flush()
        return event
