from __future__ import annotations

from app.domain.orchestration.factories.base import EventComponentsFactory
from app.domain.orchestration.factories.energy_factory import EnergyEventComponentsFactory
from app.domain.orchestration.factories.health_factory import HealthEventComponentsFactory
from app.domain.orchestration.factories.passthrough_factory import (
    PassthroughEventComponentsFactory,
)
from app.domain.events.normalization.payloads import SecurityPayload, TransportPayload
from app.domain.orchestration.factories.common import SimpleComponentsFactory


class FactoryRegistry:
    def __init__(self) -> None:
        self._factories: dict[str, EventComponentsFactory] = {
            "health": HealthEventComponentsFactory(),
            "energy": EnergyEventComponentsFactory(),
            "transport": SimpleComponentsFactory(service="transport", schema=TransportPayload),
            "security": SimpleComponentsFactory(service="security", schema=SecurityPayload),
        }

    def get(self, service: str) -> EventComponentsFactory:
        if service not in self._factories:
            return PassthroughEventComponentsFactory(service=service)
        return self._factories[service]


registry = FactoryRegistry()