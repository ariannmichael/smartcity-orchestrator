"""
Tests for factory registry
"""
import pytest

from app.domain.orchestration.registry import FactoryRegistry, registry
from app.domain.orchestration.factories.energy_factory import EnergyEventComponentsFactory
from app.domain.orchestration.factories.health_factory import HealthEventComponentsFactory
from app.domain.orchestration.factories.common import SimpleComponentsFactory
from app.domain.orchestration.factories.passthrough_factory import PassthroughEventComponentsFactory
from app.domain.events.normalization.payloads import TransportPayload, SecurityPayload


class TestFactoryRegistry:
    """Tests for FactoryRegistry"""

    def test_get_health_factory(self):
        """Test getting health factory"""
        reg = FactoryRegistry()
        factory = reg.get("health")
        
        assert isinstance(factory, HealthEventComponentsFactory)

    def test_get_energy_factory(self):
        """Test getting energy factory"""
        reg = FactoryRegistry()
        factory = reg.get("energy")
        
        assert isinstance(factory, EnergyEventComponentsFactory)

    def test_get_transport_factory(self):
        """Test getting transport factory"""
        reg = FactoryRegistry()
        factory = reg.get("transport")
        
        assert isinstance(factory, SimpleComponentsFactory)
        # Verify it uses TransportPayload
        normalizer = factory.normalizer()
        result = normalizer.normalize({"bus_id": 42})
        assert result.service == "transport"

    def test_get_security_factory(self):
        """Test getting security factory"""
        reg = FactoryRegistry()
        factory = reg.get("security")
        
        assert isinstance(factory, SimpleComponentsFactory)
        # Verify it uses SecurityPayload
        normalizer = factory.normalizer()
        result = normalizer.normalize({"alert": True})
        assert result.service == "security"

    def test_get_unknown_service_returns_passthrough(self):
        """Test that unknown service returns passthrough factory"""
        reg = FactoryRegistry()
        factory = reg.get("unknown_service")
        
        assert isinstance(factory, PassthroughEventComponentsFactory)
        normalizer = factory.normalizer()
        result = normalizer.normalize({"any": "data"})
        assert result.service == "unknown_service"

    def test_registry_singleton(self):
        """Test that the module-level registry is a singleton"""
        # Both should return the same instance
        assert registry is registry
        assert isinstance(registry, FactoryRegistry)

    def test_all_registered_services(self):
        """Test that all expected services are registered"""
        reg = FactoryRegistry()
        
        # Known services should return specific factories
        assert isinstance(reg.get("health"), HealthEventComponentsFactory)
        assert isinstance(reg.get("energy"), EnergyEventComponentsFactory)
        assert isinstance(reg.get("transport"), SimpleComponentsFactory)
        assert isinstance(reg.get("security"), SimpleComponentsFactory)
        
        # Unknown service should return passthrough
        assert isinstance(reg.get("unknown"), PassthroughEventComponentsFactory)
