"""
Tests for event ingestion
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone

from app.application.ingest import ingest_event, _persist_derived_events
from app.domain.events.types import NormalizedEvent, DerivedEventSpec
from app.infra.persistence.models.event import Event


class TestIngestEvent:
    """Tests for ingest_event function"""

    @patch('app.application.ingest.registry')
    @patch('app.application.ingest.enqueue_notification')
    def test_ingest_new_event_creates_base_and_derived(self, mock_enqueue, mock_registry, db_session):
        """Test ingesting a new event creates base and derived events"""
        # Setup mocks
        mock_factory = Mock()
        mock_normalizer = Mock()
        mock_rule_evaluator = Mock()
        
        mock_normalizer.normalize.return_value = NormalizedEvent(
            service="energy",
            timestamp=datetime.now(timezone.utc),
            raw_payload={"energy": 600.0},
            normalized_payload={"energy": 600.0, "neighborhood": "downtown"}
        )
        
        mock_rule_evaluator.evaluate.return_value = [
            DerivedEventSpec(
                service="security",
                payload={"alert": "possible_risk"},
                deduplication_key="test_key"
            )
        ]
        
        mock_factory.normalizer.return_value = mock_normalizer
        mock_factory.rule_evaluator.return_value = mock_rule_evaluator
        mock_registry.get.return_value = mock_factory
        
        # Execute
        base, derived = ingest_event("energy", {"energy": 600.0}, db_session)
        
        # Assertions
        assert isinstance(base, Event)
        assert base.service == "energy"
        assert len(derived) == 1
        assert derived[0].service == "security"
        assert derived[0].source_event_id == base.id
        mock_enqueue.assert_called_once()

    @patch('app.application.ingest.registry')
    def test_ingest_with_dedupe_key_returns_existing(self, mock_registry, db_session):
        """Test that ingesting with existing dedupe key returns existing event"""
        # Create existing event
        existing = Event(
            service="energy",
            timestamp=datetime.now(timezone.utc),
            payload={"energy": 500.0},
            normalized_payload={"energy": 500.0},
            deduplication_key="existing_key"
        )
        db_session.add(existing)
        db_session.commit()
        db_session.refresh(existing)
        
        # Create derived event
        derived = Event(
            service="security",
            payload={"alert": "test"},
            source_event_id=existing.id
        )
        db_session.add(derived)
        db_session.commit()
        
        # Execute
        base, derived_events = ingest_event("energy", {"energy": 600.0}, db_session, dedupe_key="existing_key")
        
        # Assertions
        assert base.id == existing.id
        assert len(derived_events) == 1
        assert derived_events[0].id == derived.id
        # Should not call registry or create new events
        mock_registry.get.assert_not_called()

    @patch('app.application.ingest.registry')
    @patch('app.application.ingest.enqueue_notification')
    def test_ingest_with_no_derived_events(self, mock_enqueue, mock_registry, db_session):
        """Test ingesting event that produces no derived events"""
        mock_factory = Mock()
        mock_normalizer = Mock()
        mock_rule_evaluator = Mock()
        
        mock_normalizer.normalize.return_value = NormalizedEvent(
            service="energy",
            timestamp=datetime.now(timezone.utc),
            raw_payload={"energy": 400.0},
            normalized_payload={"energy": 400.0}
        )
        
        mock_rule_evaluator.evaluate.return_value = []
        
        mock_factory.normalizer.return_value = mock_normalizer
        mock_factory.rule_evaluator.return_value = mock_rule_evaluator
        mock_registry.get.return_value = mock_factory
        
        # Execute
        base, derived = ingest_event("energy", {"energy": 400.0}, db_session)
        
        # Assertions
        assert isinstance(base, Event)
        assert len(derived) == 0
        mock_enqueue.assert_not_called()

    @patch('app.application.ingest.registry')
    @patch('app.application.ingest.enqueue_notification')
    def test_ingest_sets_deduplication_key(self, mock_enqueue, mock_registry, db_session):
        """Test that deduplication key is set on base event"""
        mock_factory = Mock()
        mock_normalizer = Mock()
        mock_rule_evaluator = Mock()
        
        mock_normalizer.normalize.return_value = NormalizedEvent(
            service="energy",
            timestamp=datetime.now(timezone.utc),
            raw_payload={"energy": 500.0},
            normalized_payload={"energy": 500.0}
        )
        
        mock_rule_evaluator.evaluate.return_value = []
        
        mock_factory.normalizer.return_value = mock_normalizer
        mock_factory.rule_evaluator.return_value = mock_rule_evaluator
        mock_registry.get.return_value = mock_factory
        
        # Execute
        base, _ = ingest_event("energy", {"energy": 500.0}, db_session, dedupe_key="test_key")
        
        # Assertions
        assert base.deduplication_key == "test_key"

    @patch('app.application.ingest.registry')
    @patch('app.application.ingest.enqueue_notification')
    def test_ingest_commits_transaction(self, mock_enqueue, mock_registry, db_session):
        """Test that ingest commits the transaction"""
        mock_factory = Mock()
        mock_normalizer = Mock()
        mock_rule_evaluator = Mock()
        
        mock_normalizer.normalize.return_value = NormalizedEvent(
            service="energy",
            timestamp=datetime.now(timezone.utc),
            raw_payload={"energy": 500.0},
            normalized_payload={"energy": 500.0}
        )
        
        mock_rule_evaluator.evaluate.return_value = []
        
        mock_factory.normalizer.return_value = mock_normalizer
        mock_factory.rule_evaluator.return_value = mock_rule_evaluator
        mock_registry.get.return_value = mock_factory
        
        # Execute
        ingest_event("energy", {"energy": 500.0}, db_session)
        
        # Verify commit was called (events should be persisted)
        # We can verify by querying the database
        from sqlalchemy import select
        events = db_session.execute(select(Event)).scalars().all()
        assert len(events) == 1


class TestPersistDerivedEvents:
    """Tests for _persist_derived_events function"""

    @patch('app.application.ingest.enqueue_notification')
    def test_persist_derived_events_creates_events(self, mock_enqueue, db_session):
        """Test that _persist_derived_events creates derived events"""
        normalized = NormalizedEvent(
            service="energy",
            timestamp=datetime.now(timezone.utc),
            raw_payload={"energy": 600.0},
            normalized_payload={"energy": 600.0}
        )
        
        mock_factory = Mock()
        mock_rule_evaluator = Mock()
        mock_rule_evaluator.evaluate.return_value = [
            DerivedEventSpec(
                service="security",
                payload={"alert": "test"},
                deduplication_key="derived_key"
            ),
            DerivedEventSpec(
                service="transport",
                payload={"action": "test"},
            )
        ]
        mock_factory.rule_evaluator.return_value = mock_rule_evaluator
        
        # Use a simple UUID for SQLite
        import uuid
        base_id = uuid.uuid4()
        
        # Execute
        derived_events = _persist_derived_events(normalized, mock_factory, base_id, db_session)
        
        # Assertions
        assert len(derived_events) == 2
        assert derived_events[0].service == "security"
        assert derived_events[0].source_event_id == base_id
        assert derived_events[0].deduplication_key == "derived_key"
        assert derived_events[1].service == "transport"
        assert derived_events[1].deduplication_key is None
        assert mock_enqueue.call_count == 2

    @patch('app.application.ingest.enqueue_notification')
    def test_persist_derived_events_with_no_specs(self, mock_enqueue, db_session):
        """Test _persist_derived_events with no derived specs"""
        normalized = NormalizedEvent(
            service="energy",
            timestamp=datetime.now(timezone.utc),
            raw_payload={"energy": 400.0},
            normalized_payload={"energy": 400.0}
        )
        
        mock_factory = Mock()
        mock_rule_evaluator = Mock()
        mock_rule_evaluator.evaluate.return_value = []
        mock_factory.rule_evaluator.return_value = mock_rule_evaluator
        
        import uuid
        base_id = uuid.uuid4()
        
        # Execute
        derived_events = _persist_derived_events(normalized, mock_factory, base_id, db_session)
        
        # Assertions
        assert len(derived_events) == 0
        mock_enqueue.assert_not_called()
