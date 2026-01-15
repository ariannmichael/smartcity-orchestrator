"""
Tests for repository classes
"""
import pytest
from datetime import datetime, timezone

from app.infra.persistence.repositories.event_repo import EventRepository
from app.infra.persistence.repositories.outbox_repo import OutboxRepository
from app.infra.persistence.models.event import Event
from app.infra.persistence.models.outbox import OutboxMessage


class TestEventRepository:
    """Tests for EventRepository"""

    def test_add_event(self, db_session):
        """Test adding an event through repository"""
        repo = EventRepository(db_session)
        event = Event(
            service="energy",
            timestamp=datetime.now(timezone.utc),
            payload={"energy": 500.0},
            normalized_payload={"energy": 500.0}
        )
        
        result = repo.add(event)
        
        assert result == event
        assert event in db_session
        # Verify flush was called (event should have ID)
        assert event.id is not None

    def test_add_multiple_events(self, db_session):
        """Test adding multiple events"""
        repo = EventRepository(db_session)
        events = [
            Event(
                service="energy",
                timestamp=datetime.now(timezone.utc),
                payload={"energy": 500.0 + i},
                normalized_payload={"energy": 500.0 + i}
            )
            for i in range(3)
        ]
        
        for event in events:
            repo.add(event)
        
        # After flush, events are no longer in 'new', verify they have IDs
        assert all(event.id is not None for event in events)
        assert len(events) == 3


class TestOutboxRepository:
    """Tests for OutboxRepository"""

    def test_add_outbox_message(self, db_session):
        """Test adding an outbox message through repository"""
        repo = OutboxRepository(db_session)
        msg = OutboxMessage(
            topic="event.energy",
            payload={"energy": 500.0},
            status="pending",
            attempts=0
        )
        
        result = repo.add(msg)
        
        assert result == msg
        assert msg in db_session
        # Verify flush was called (message should have ID)
        assert msg.id is not None
