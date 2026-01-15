import os
import time
from datetime import datetime, timezone

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.infra.persistence.models.outbox import OutboxMessage

POLL_SECONDS = float(os.getenv("OUTBOX_POLL_SECONDS", "1.0"))
BATCH_SIZE = int(os.getenv("OUTBOX_BATCH_SIZE", "20"))
MAX_ATTEMPTS = int(os.getenv("OUTBOX_MAX_ATTEMPTS", "5"))


def publish(topic: str, payload: dict) -> None:
    print(f"Publishing message to topic: {topic} with payload: {payload}")


def main() -> None:
    engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

    print("Starting outbox worker")
    while True:
        db = SessionLocal()
        try:
            msgs = db.execute(
                select(OutboxMessage)
                .where(OutboxMessage.status == "pending")
                .order_by(OutboxMessage.created_at.asc())
                .limit(BATCH_SIZE)
            ).scalars().all()

            if not msgs:
                time.sleep(POLL_SECONDS)
                continue

            for msg in msgs:
                if msg.attempts >= MAX_ATTEMPTS:
                    msg.status = "failed"
                    continue

                try:
                    publish(msg.topic, msg.payload)
                    msg.status = "sent"
                    msg.published_at = datetime.now(timezone.utc)
                except Exception as e:
                    msg.attempts += 1

            db.commit()
        except Exception as e:
            print(f"Error processing outbox messages: {e}")
            db.rollback()
        finally:
            db.close()
        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    main()