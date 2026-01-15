from __future__ import annotations

from typing import Dict, Type

from app.domain.orchestration.factories.base import EventComponentsFactory
from app.domain.orchestration.factories.energy_factory import EnergyEventComponentsFactory
from app.domain.orchestration.factories.health_factory import HealthEventComponentsFactory
from app.domain.orchestration.factories.passthrough_factory import (
    PassthroughEventComponentsFactory,
)


_FACTORY_REGISTRY: Dict[str, Type[EventComponentsFactory]] = {
    "health": HealthEventComponentsFactory,
    "energy": EnergyEventComponentsFactory,
}


def get_factory(service: str) -> EventComponentsFactory:
    factory_cls = _FACTORY_REGISTRY.get(service, PassthroughEventComponentsFactory)
    return factory_cls(service=service)
