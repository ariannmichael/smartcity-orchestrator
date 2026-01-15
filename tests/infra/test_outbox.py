"""
Tests for outbox functionality
"""
import pytest
from datetime import datetime, timezone
from unittest.mock import patch, Mock

from app.infra.outbox.enqueue import enqueue_notification, topic_for_service
from app.infra.persistence.models.outbox import OutboxMessage


class TestTopicForService:
    """Tests for topic_for_service function"""

    def test_topic_for_service_formats_correctly(self):
        """Test that topic_for_service formats topic name correctly"""
        assert topic_for_service("energy") == "event.energy"
        assert topic_for_service("health") == "event.health"
        assert topic_for_service("transport") == "event.transport"
        assert topic_for_service("security") == "event.security"

    def test_topic_for_service_with_custom_service(self):
        """Test topic_for_service with custom service name"""
        assert topic_for_service("custom_service") == "event.custom_service"


class TestEnqueueNotification:
    """Tests for enqueue_notification function"""

    def test_enqueue_notification_creates_outbox_message(self, db_session):
        """Test that enqueue_notification creates outbox message"""
        msg = enqueue_notification(db_session, "energy", {"energy": 600.0})
        
        assert isinstance(msg, OutboxMessage)
        assert msg.topic == "event.energy"
        assert msg.payload == {"energy": 600.0}
        assert msg.status == "pending"
        assert msg.attempts == 0
        assert msg.published_at is None
        assert isinstance(msg.created_at, datetime)

    def test_enqueue_notification_persists_to_db(self, db_session):
        """Test that enqueue_notification persists message to database"""
        msg = enqueue_notification(db_session, "health", {"patient_id": 123})
        
        # Verify it's in the database
        from sqlalchemy import select
        messages = db_session.execute(
            select(OutboxMessage).where(OutboxMessage.id == msg.id)
        ).scalars().all()
        
        assert len(messages) == 1
        assert messages[0].topic == "event.health"
        assert messages[0].payload == {"patient_id": 123}

    def test_enqueue_notification_commits_transaction(self, db_session):
        """Test that enqueue_notification commits the transaction"""
        msg = enqueue_notification(db_session, "energy", {"test": "data"})
        
        # Verify commit was called by checking the message has an ID
        assert msg.id is not None

    def test_enqueue_notification_with_different_services(self, db_session):
        """Test enqueue_notification with different service types"""
        services = ["energy", "health", "transport", "security"]
        
        for service in services:
            msg = enqueue_notification(db_session, service, {"test": "data"})
            assert msg.topic == f"event.{service}"

    def test_enqueue_notification_with_complex_payload(self, db_session):
        """Test enqueue_notification with complex payload structure"""
        complex_payload = {
            "nested": {
                "data": [1, 2, 3],
                "metadata": {
                    "source": "test",
                    "timestamp": "2024-01-01T00:00:00Z"
                }
            },
            "array": ["item1", "item2"]
        }
        
        msg = enqueue_notification(db_session, "energy", complex_payload)
        
        assert msg.payload == complex_payload
        assert msg.payload["nested"]["data"] == [1, 2, 3]
