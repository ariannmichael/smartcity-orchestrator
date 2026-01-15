from __future__ import annotations

from sqlalchemy.orm import Session

from app.infra.persistence.models.outbox import Outbox


class OutboxRepository:
    def __init__(self, db: Session):
        self._db = db

    def add(self, entry: Outbox) -> Outbox:
        self._db.add(entry)
        self._db.flush()
        return entry
