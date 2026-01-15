"""
Tests for API schemas
"""
import pytest
from datetime import datetime, timezone
from uuid import uuid4

from app.api.schemas import IngestResponse, EventOut
from app.infra.persistence.models.event import Event


class TestIngestResponse:
    """Tests for IngestResponse schema"""

    def test_ingest_response_creation(self):
        """Test creating IngestResponse with valid data"""
        base_id = uuid4()
        derived_ids = [uuid4(), uuid4()]
        
        response = IngestResponse(
            stored_event_id=base_id,
            derived_events=derived_ids
        )
        
        assert response.stored_event_id == base_id
        assert response.derived_events == derived_ids
        assert len(response.derived_events) == 2

    def test_ingest_response_with_empty_derived_events(self):
        """Test IngestResponse with no derived events"""
        base_id = uuid4()
        
        response = IngestResponse(
            stored_event_id=base_id,
            derived_events=[]
        )
        
        assert response.stored_event_id == base_id
        assert response.derived_events == []

    def test_ingest_response_serialization(self):
        """Test that IngestResponse can be serialized to dict"""
        base_id = uuid4()
        derived_ids = [uuid4()]
        
        response = IngestResponse(
            stored_event_id=base_id,
            derived_events=derived_ids
        )
        
        data = response.model_dump()
        assert "stored_event_id" in data
        assert "derived_events" in data
        assert isinstance(data["derived_events"], list)


class TestEventOut:
    """Tests for EventOut schema"""

    def test_event_out_from_event_model(self, db_session):
        """Test creating EventOut from Event model"""
        event = Event(
            service="energy",
            timestamp=datetime.now(timezone.utc),
            payload={"energy": 500.0},
            normalized_payload={"energy": 500.0, "neighborhood": "downtown"},
            deduplication_key="test_key"
        )
        db_session.add(event)
        db_session.commit()
        db_session.refresh(event)
        
        event_out = EventOut.model_validate(event)
        
        assert event_out.id == event.id
        assert event_out.service == "energy"
        assert event_out.payload == {"energy": 500.0}
        assert event_out.normalized_payload == {"energy": 500.0, "neighborhood": "downtown"}
        assert event_out.deduplication_key == "test_key"
        assert event_out.source_event_id is None

    def test_event_out_with_source_event_id(self, db_session):
        """Test EventOut with source_event_id"""
        base_event = Event(
            service="energy",
            timestamp=datetime.now(timezone.utc),
            payload={"energy": 600.0},
            normalized_payload={"energy": 600.0}
        )
        db_session.add(base_event)
        db_session.flush()
        
        derived_event = Event(
            service="security",
            payload={"alert": "test"},
            source_event_id=base_event.id
        )
        db_session.add(derived_event)
        db_session.commit()
        db_session.refresh(derived_event)
        
        event_out = EventOut.model_validate(derived_event)
        
        assert event_out.source_event_id == base_event.id
        assert event_out.service == "security"

    def test_event_out_without_normalized_payload(self, db_session):
        """Test EventOut with None normalized_payload"""
        event = Event(
            service="security",
            timestamp=datetime.now(timezone.utc),
            payload={"alert": "test"},
            normalized_payload=None
        )
        db_session.add(event)
        db_session.commit()
        db_session.refresh(event)
        
        event_out = EventOut.model_validate(event)
        
        assert event_out.normalized_payload is None

    def test_event_out_serialization(self, db_session):
        """Test that EventOut can be serialized to dict"""
        event = Event(
            service="energy",
            timestamp=datetime.now(timezone.utc),
            payload={"energy": 500.0},
            normalized_payload={"energy": 500.0}
        )
        db_session.add(event)
        db_session.commit()
        db_session.refresh(event)
        
        event_out = EventOut.model_validate(event)
        data = event_out.model_dump()
        
        assert "id" in data
        assert "service" in data
        assert "timestamp" in data
        assert "payload" in data
        assert "normalized_payload" in data
        assert "created_at" in data
        # Pydantic serializes datetime to ISO format strings
        assert isinstance(data["timestamp"], (str, datetime))
        assert isinstance(data["created_at"], (str, datetime))
