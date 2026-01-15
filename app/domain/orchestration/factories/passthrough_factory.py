from __future__ import annotations

from app.domain.events.normalization.payloads import BasePayload
from app.domain.events.normalization.pydantic import PydanticEventNormalizer
from typing import List

from app.domain.events.rules.base import RuleEvaluator
from app.domain.events.types import DerivedEventSpec, NormalizedEvent
from app.domain.orchestration.factories.base import EventComponentsFactory


class PassthroughRuleEvaluator(RuleEvaluator):
    def evaluate(self, normalized_event: NormalizedEvent) -> List[DerivedEventSpec]:
        return []


class PassthroughEventComponentsFactory(EventComponentsFactory):
    def __init__(self, service: str):
        self._service = service

    def normalizer(self) -> PydanticEventNormalizer:
        return PydanticEventNormalizer(service=self._service, schema=BasePayload)

    def rule_evaluator(self) -> RuleEvaluator:
        return PassthroughRuleEvaluator()
