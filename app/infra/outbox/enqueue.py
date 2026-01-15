from sqlalchemy.orm import Session
from app.infra.persistence.models.outbox import OutboxMessage
from datetime import datetime, timezone


def topic_for_service(service: str) -> str:
    return f"event.{service}"


def enqueue_notification(db: Session, service: str, payload: dict) -> OutboxMessage:
    msg = OutboxMessage(
        topic=topic_for_service(service),
        payload=payload,
        status="pending",
        attempts=0,
        published_at=None,
        created_at=datetime.now(timezone.utc)
    )
    db.add(msg)
    db.commit()
    return msg