"""
Tests for event normalizers
"""
import pytest
from datetime import datetime
from pydantic import ValidationError

from app.domain.events.normalization.pydantic import PydanticEventNormalizer
from app.domain.events.normalization.payloads import (
    EnergyPayload,
    HealthPayload,
    BasePayload,
    TransportPayload,
    SecurityPayload
)
from app.domain.events.types import NormalizedEvent


class TestPydanticEventNormalizer:
    """Tests for PydanticEventNormalizer"""

    def test_normalize_valid_energy_payload(self):
        """Test normalizing a valid energy payload"""
        normalizer = PydanticEventNormalizer(service="energy", schema=EnergyPayload)
        payload = {"energy": 500.0, "neighborhood": "downtown"}
        
        result = normalizer.normalize(payload)
        
        assert isinstance(result, NormalizedEvent)
        assert result.service == "energy"
        assert result.raw_payload == payload
        assert result.normalized_payload["energy"] == 500.0
        assert result.normalized_payload["neighborhood"] == "downtown"
        assert isinstance(result.timestamp, datetime)

    def test_normalize_valid_health_payload(self):
        """Test normalizing a valid health payload"""
        normalizer = PydanticEventNormalizer(service="health", schema=HealthPayload)
        payload = {"patient_id": 123, "alert": "emergency", "location": "room_5"}
        
        result = normalizer.normalize(payload)
        
        assert isinstance(result, NormalizedEvent)
        assert result.service == "health"
        assert result.raw_payload == payload
        assert result.normalized_payload["patient_id"] == 123
        assert result.normalized_payload["alert"] == "emergency"
        assert result.normalized_payload["location"] == "room_5"

    def test_normalize_invalid_payload_falls_back_to_raw(self):
        """Test that invalid payloads fall back to raw payload"""
        normalizer = PydanticEventNormalizer(service="energy", schema=EnergyPayload)
        payload = {"invalid": "data", "energy": "not_a_number"}
        
        result = normalizer.normalize(payload)
        
        assert isinstance(result, NormalizedEvent)
        assert result.service == "energy"
        assert result.raw_payload == payload
        # Should fall back to raw payload when validation fails
        assert result.normalized_payload == payload

    def test_normalize_with_extra_fields(self):
        """Test normalizing payload with extra fields (should be allowed)"""
        normalizer = PydanticEventNormalizer(service="energy", schema=EnergyPayload)
        payload = {
            "energy": 500.0,
            "neighborhood": "downtown",
            "extra_field": "should_be_included"
        }
        
        result = normalizer.normalize(payload)
        
        assert result.normalized_payload["energy"] == 500.0
        assert result.normalized_payload["extra_field"] == "should_be_included"

    def test_normalize_transport_payload(self):
        """Test normalizing transport payload"""
        normalizer = PydanticEventNormalizer(service="transport", schema=TransportPayload)
        payload = {"bus_id": 42, "lat": 40.7128, "lon": -74.0060}
        
        result = normalizer.normalize(payload)
        
        assert result.service == "transport"
        assert result.normalized_payload["bus_id"] == 42
        assert result.normalized_payload["lat"] == 40.7128
        assert result.normalized_payload["lon"] == -74.0060

    def test_normalize_security_payload(self):
        """Test normalizing security payload"""
        normalizer = PydanticEventNormalizer(service="security", schema=SecurityPayload)
        payload = {"alert": True, "camera_trigger": "motion_detected"}
        
        result = normalizer.normalize(payload)
        
        assert result.service == "security"
        assert result.normalized_payload["alert"] is True
        assert result.normalized_payload["camera_trigger"] == "motion_detected"

    def test_normalize_base_payload(self):
        """Test normalizing with base payload schema"""
        normalizer = PydanticEventNormalizer(service="unknown", schema=BasePayload)
        payload = {"any": "data", "structure": "works"}
        
        result = normalizer.normalize(payload)
        
        assert result.service == "unknown"
        assert result.normalized_payload == payload

    def test_normalize_empty_payload(self):
        """Test normalizing empty payload"""
        normalizer = PydanticEventNormalizer(service="energy", schema=EnergyPayload)
        payload = {}
        
        result = normalizer.normalize(payload)
        
        assert result.service == "energy"
        assert result.raw_payload == {}
        # Pydantic will include optional fields with None values
        assert "energy" in result.normalized_payload or result.normalized_payload == {}
