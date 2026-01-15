"""
Tests for rule evaluators
"""
import pytest
from datetime import datetime

from app.domain.events.rules.energy import EnergyRuleEvaluator
from app.domain.events.rules.health import HealthRuleEvaluator
from app.domain.events.types import NormalizedEvent, DerivedEventSpec
from app.domain.orchestration.factories.common import NoopRuleEvaluator
from app.domain.orchestration.factories.passthrough_factory import PassthroughRuleEvaluator


class TestEnergyRuleEvaluator:
    """Tests for EnergyRuleEvaluator"""

    def test_evaluate_below_threshold_returns_empty(self):
        """Test that energy below threshold returns no derived events"""
        evaluator = EnergyRuleEvaluator()
        event = NormalizedEvent(
            service="energy",
            timestamp=datetime.now(),
            raw_payload={"energy": 400.0, "neighborhood": "downtown"},
            normalized_payload={"energy": 400.0, "neighborhood": "downtown"}
        )
        
        result = evaluator.evaluate(event)
        
        assert result == []

    def test_evaluate_at_threshold_returns_empty(self):
        """Test that energy at threshold returns no derived events"""
        evaluator = EnergyRuleEvaluator()
        event = NormalizedEvent(
            service="energy",
            timestamp=datetime.now(),
            raw_payload={"energy": 500.0, "neighborhood": "downtown"},
            normalized_payload={"energy": 500.0, "neighborhood": "downtown"}
        )
        
        result = evaluator.evaluate(event)
        
        assert result == []

    def test_evaluate_above_threshold_returns_security_event(self):
        """Test that energy above threshold returns security event"""
        evaluator = EnergyRuleEvaluator()
        event = NormalizedEvent(
            service="energy",
            timestamp=datetime.now(),
            raw_payload={"energy": 600.0, "neighborhood": "downtown"},
            normalized_payload={"energy": 600.0, "neighborhood": "downtown"}
        )
        
        result = evaluator.evaluate(event)
        
        assert len(result) == 1
        assert isinstance(result[0], DerivedEventSpec)
        assert result[0].service == "security"
        assert result[0].payload["alert"] == "possible_risk"
        assert result[0].payload["reason"] == "critical_energy_usage"
        assert result[0].payload["neighborhood"] == "downtown"
        assert result[0].payload["energy"] == 600.0
        assert result[0].deduplication_key == "critical_energy_usage_downtown"

    def test_evaluate_missing_energy_returns_empty(self):
        """Test that missing energy field returns no derived events"""
        evaluator = EnergyRuleEvaluator()
        event = NormalizedEvent(
            service="energy",
            timestamp=datetime.now(),
            raw_payload={"neighborhood": "downtown"},
            normalized_payload={"neighborhood": "downtown"}
        )
        
        result = evaluator.evaluate(event)
        
        assert result == []

    def test_evaluate_none_energy_returns_empty(self):
        """Test that None energy returns no derived events"""
        evaluator = EnergyRuleEvaluator()
        event = NormalizedEvent(
            service="energy",
            timestamp=datetime.now(),
            raw_payload={"energy": None, "neighborhood": "downtown"},
            normalized_payload={"energy": None, "neighborhood": "downtown"}
        )
        
        result = evaluator.evaluate(event)
        
        assert result == []

    def test_evaluate_missing_neighborhood_still_creates_event(self):
        """Test that missing neighborhood still creates security event"""
        evaluator = EnergyRuleEvaluator()
        event = NormalizedEvent(
            service="energy",
            timestamp=datetime.now(),
            raw_payload={"energy": 600.0},
            normalized_payload={"energy": 600.0}
        )
        
        result = evaluator.evaluate(event)
        
        assert len(result) == 1
        assert result[0].payload["neighborhood"] is None
        assert result[0].deduplication_key == "critical_energy_usage_None"


class TestHealthRuleEvaluator:
    """Tests for HealthRuleEvaluator"""

    def test_evaluate_non_emergency_returns_empty(self):
        """Test that non-emergency alerts return no derived events"""
        evaluator = HealthRuleEvaluator()
        event = NormalizedEvent(
            service="health",
            timestamp=datetime.now(),
            raw_payload={"patient_id": 123, "alert": "routine", "location": "room_5"},
            normalized_payload={"patient_id": 123, "alert": "routine", "location": "room_5"}
        )
        
        result = evaluator.evaluate(event)
        
        assert result == []

    def test_evaluate_emergency_returns_transport_and_security(self):
        """Test that emergency alerts return transport and security events"""
        evaluator = HealthRuleEvaluator()
        event = NormalizedEvent(
            service="health",
            timestamp=datetime.now(),
            raw_payload={"patient_id": 123, "alert": "emergency", "location": "room_5"},
            normalized_payload={"patient_id": 123, "alert": "emergency", "location": "room_5"}
        )
        
        result = evaluator.evaluate(event)
        
        assert len(result) == 2
        
        # Check transport event
        transport_event = next(e for e in result if e.service == "transport")
        assert transport_event.payload["action"] == "dispatch_nearest_vehicle"
        assert transport_event.payload["reason"] == "health_emergency"
        assert transport_event.payload["location"] == "room_5"
        assert transport_event.payload["patient_id"] == 123
        assert transport_event.deduplication_key == "health_emergency_123"
        
        # Check security event
        security_event = next(e for e in result if e.service == "security")
        assert security_event.payload["priority"] == "high"
        assert security_event.payload["action"] == "escort_and_clear_traffic"
        assert security_event.payload["reason"] == "health_emergency"
        assert security_event.payload["location"] == "room_5"
        assert security_event.payload["patient_id"] == 123
        assert security_event.deduplication_key == "health_emergency_123"

    def test_evaluate_missing_alert_returns_empty(self):
        """Test that missing alert field returns no derived events"""
        evaluator = HealthRuleEvaluator()
        event = NormalizedEvent(
            service="health",
            timestamp=datetime.now(),
            raw_payload={"patient_id": 123, "location": "room_5"},
            normalized_payload={"patient_id": 123, "location": "room_5"}
        )
        
        result = evaluator.evaluate(event)
        
        assert result == []

    def test_evaluate_missing_patient_id_still_creates_events(self):
        """Test that missing patient_id still creates events"""
        evaluator = HealthRuleEvaluator()
        event = NormalizedEvent(
            service="health",
            timestamp=datetime.now(),
            raw_payload={"alert": "emergency", "location": "room_5"},
            normalized_payload={"alert": "emergency", "location": "room_5"}
        )
        
        result = evaluator.evaluate(event)
        
        assert len(result) == 2
        assert result[0].payload["patient_id"] is None
        assert result[0].deduplication_key == "health_emergency_None"


class TestNoopRuleEvaluator:
    """Tests for NoopRuleEvaluator"""

    def test_evaluate_always_returns_empty(self):
        """Test that NoopRuleEvaluator always returns empty list"""
        evaluator = NoopRuleEvaluator()
        event = NormalizedEvent(
            service="any",
            timestamp=datetime.now(),
            raw_payload={"any": "data"},
            normalized_payload={"any": "data"}
        )
        
        result = evaluator.evaluate(event)
        
        assert result == []


class TestPassthroughRuleEvaluator:
    """Tests for PassthroughRuleEvaluator"""

    def test_evaluate_always_returns_empty(self):
        """Test that PassthroughRuleEvaluator always returns empty list"""
        evaluator = PassthroughRuleEvaluator()
        event = NormalizedEvent(
            service="any",
            timestamp=datetime.now(),
            raw_payload={"any": "data"},
            normalized_payload={"any": "data"}
        )
        
        result = evaluator.evaluate(event)
        
        assert result == []
