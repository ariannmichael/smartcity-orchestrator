from __future__ import annotations

from app.domain.events.normalization.payloads import EnergyPayload
from app.domain.events.normalization.pydantic import PydanticEventNormalizer
from app.domain.events.rules.energy import EnergyRuleEvaluator
from app.domain.orchestration.factories.base import EventComponentsFactory


class EnergyEventComponentsFactory(EventComponentsFactory):
    def __init__(self, service: str = "energy"):
        self._service = service

    def normalizer(self) -> PydanticEventNormalizer:
        return PydanticEventNormalizer(service=self._service, schema=EnergyPayload)

    def rule_evaluator(self) -> EnergyRuleEvaluator:
        return EnergyRuleEvaluator()
