from __future__ import annotations

from app.domain.events.normalization.payloads import HealthPayload
from app.domain.events.normalization.pydantic import PydanticEventNormalizer
from app.domain.events.rules.health import HealthRuleEvaluator
from app.domain.orchestration.factories.base import EventComponentsFactory


class HealthEventComponentsFactory(EventComponentsFactory):
    def __init__(self, service: str = "health"):
        self._service = service

    def normalizer(self) -> PydanticEventNormalizer:
        return PydanticEventNormalizer(service=self._service, schema=HealthPayload)

    def rule_evaluator(self) -> HealthRuleEvaluator:
        return HealthRuleEvaluator()
