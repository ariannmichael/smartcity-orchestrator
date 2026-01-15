"""
Tests for event component factories
"""
import pytest

from app.domain.orchestration.factories.energy_factory import EnergyEventComponentsFactory
from app.domain.orchestration.factories.health_factory import HealthEventComponentsFactory
from app.domain.orchestration.factories.common import SimpleComponentsFactory, NoopRuleEvaluator
from app.domain.orchestration.factories.passthrough_factory import (
    PassthroughEventComponentsFactory,
    PassthroughRuleEvaluator
)
from app.domain.events.normalization.payloads import (
    EnergyPayload,
    HealthPayload,
    TransportPayload,
    SecurityPayload,
    BasePayload
)
from app.domain.events.normalization.pydantic import PydanticEventNormalizer


class TestEnergyEventComponentsFactory:
    """Tests for EnergyEventComponentsFactory"""

    def test_normalizer_returns_pydantic_normalizer_with_energy_schema(self):
        """Test that normalizer returns correct normalizer"""
        factory = EnergyEventComponentsFactory()
        normalizer = factory.normalizer()
        
        assert isinstance(normalizer, PydanticEventNormalizer)
        # Can't directly check schema type, but can verify it works
        result = normalizer.normalize({"energy": 500.0})
        assert result.service == "energy"

    def test_rule_evaluator_returns_energy_rule_evaluator(self):
        """Test that rule_evaluator returns EnergyRuleEvaluator"""
        factory = EnergyEventComponentsFactory()
        evaluator = factory.rule_evaluator()
        
        from app.domain.events.rules.energy import EnergyRuleEvaluator
        assert isinstance(evaluator, EnergyRuleEvaluator)

    def test_custom_service_name(self):
        """Test factory with custom service name"""
        factory = EnergyEventComponentsFactory(service="custom_energy")
        normalizer = factory.normalizer()
        
        result = normalizer.normalize({"energy": 500.0})
        assert result.service == "custom_energy"


class TestHealthEventComponentsFactory:
    """Tests for HealthEventComponentsFactory"""

    def test_normalizer_returns_pydantic_normalizer_with_health_schema(self):
        """Test that normalizer returns correct normalizer"""
        factory = HealthEventComponentsFactory()
        normalizer = factory.normalizer()
        
        assert isinstance(normalizer, PydanticEventNormalizer)
        result = normalizer.normalize({"patient_id": 123})
        assert result.service == "health"

    def test_rule_evaluator_returns_health_rule_evaluator(self):
        """Test that rule_evaluator returns HealthRuleEvaluator"""
        factory = HealthEventComponentsFactory()
        evaluator = factory.rule_evaluator()
        
        from app.domain.events.rules.health import HealthRuleEvaluator
        assert isinstance(evaluator, HealthRuleEvaluator)

    def test_custom_service_name(self):
        """Test factory with custom service name"""
        factory = HealthEventComponentsFactory(service="custom_health")
        normalizer = factory.normalizer()
        
        result = normalizer.normalize({"patient_id": 123})
        assert result.service == "custom_health"


class TestSimpleComponentsFactory:
    """Tests for SimpleComponentsFactory"""

    def test_normalizer_returns_pydantic_normalizer_with_custom_schema(self):
        """Test that normalizer uses provided schema"""
        factory = SimpleComponentsFactory(service="transport", schema=TransportPayload)
        normalizer = factory.normalizer()
        
        assert isinstance(normalizer, PydanticEventNormalizer)
        result = normalizer.normalize({"bus_id": 42})
        assert result.service == "transport"

    def test_rule_evaluator_returns_noop_evaluator(self):
        """Test that rule_evaluator returns NoopRuleEvaluator"""
        factory = SimpleComponentsFactory(service="transport", schema=TransportPayload)
        evaluator = factory.rule_evaluator()
        
        assert isinstance(evaluator, NoopRuleEvaluator)

    def test_with_security_schema(self):
        """Test factory with security schema"""
        factory = SimpleComponentsFactory(service="security", schema=SecurityPayload)
        normalizer = factory.normalizer()
        
        result = normalizer.normalize({"alert": True})
        assert result.service == "security"


class TestPassthroughEventComponentsFactory:
    """Tests for PassthroughEventComponentsFactory"""

    def test_normalizer_returns_pydantic_normalizer_with_base_schema(self):
        """Test that normalizer uses BasePayload schema"""
        factory = PassthroughEventComponentsFactory(service="unknown")
        normalizer = factory.normalizer()
        
        assert isinstance(normalizer, PydanticEventNormalizer)
        result = normalizer.normalize({"any": "data"})
        assert result.service == "unknown"

    def test_rule_evaluator_returns_passthrough_evaluator(self):
        """Test that rule_evaluator returns PassthroughRuleEvaluator"""
        factory = PassthroughEventComponentsFactory(service="unknown")
        evaluator = factory.rule_evaluator()
        
        assert isinstance(evaluator, PassthroughRuleEvaluator)

    def test_with_different_service_names(self):
        """Test factory with different service names"""
        factory1 = PassthroughEventComponentsFactory(service="service1")
        factory2 = PassthroughEventComponentsFactory(service="service2")
        
        result1 = factory1.normalizer().normalize({"data": "test"})
        result2 = factory2.normalizer().normalize({"data": "test"})
        
        assert result1.service == "service1"
        assert result2.service == "service2"
