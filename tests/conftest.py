"""
Pytest configuration and shared fixtures
"""
import pytest
from datetime import datetime, timezone
from unittest.mock import Mock, MagicMock
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.dialects.sqlite.base import SQLiteTypeCompiler

# Patch JSONB to work with SQLite
def visit_JSONB(self, type_, **kw):
    return "JSON"

# Patch UUID to work with SQLite (store as TEXT)
def visit_UUID(self, type_, **kw):
    return "TEXT"

SQLiteTypeCompiler.visit_JSONB = visit_JSONB
SQLiteTypeCompiler.visit_UUID = visit_UUID

from app.core.db import Base
from app.infra.persistence.models.event import Event
from app.infra.persistence.models.outbox import OutboxMessage


@pytest.fixture
def db_session():
    """Create an in-memory SQLite database session for testing"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)


@pytest.fixture
def mock_db_session():
    """Create a mock database session"""
    session = Mock(spec=Session)
    session.add = Mock()
    session.commit = Mock()
    session.flush = Mock()
    session.refresh = Mock()
    session.execute = Mock()
    return session


@pytest.fixture
def sample_payload():
    """Sample payload for testing"""
    return {
        "energy": 600.0,
        "neighborhood": "downtown"
    }


@pytest.fixture
def sample_health_payload():
    """Sample health payload for testing"""
    return {
        "patient_id": 123,
        "alert": "emergency",
        "location": "hospital_room_5"
    }


@pytest.fixture
def sample_event(db_session):
    """Create a sample event in the database"""
    event = Event(
        service="energy",
        timestamp=datetime.now(timezone.utc),
        payload={"energy": 500.0},
        normalized_payload={"energy": 500.0, "neighborhood": "downtown"},
        deduplication_key="test_key_123"
    )
    db_session.add(event)
    db_session.commit()
    db_session.refresh(event)
    return event


@pytest.fixture
def sample_outbox_message(db_session):
    """Create a sample outbox message in the database"""
    msg = OutboxMessage(
        topic="event.energy",
        payload={"test": "data"},
        status="pending",
        attempts=0
    )
    db_session.add(msg)
    db_session.commit()
    db_session.refresh(msg)
    return msg
