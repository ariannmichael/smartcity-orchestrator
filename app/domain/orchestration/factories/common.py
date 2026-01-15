from __future__ import annotations

from typing import List, Type
from pydantic import BaseModel

from app.domain.events.types import (
    DerivedEventSpec,
    NormalizedEvent,
)
from app.domain.orchestration.factories.base import EventComponentsFactory
from app.domain.events.normalization.pydantic import PydanticEventNormalizer
from app.domain.events.normalization.base import EventNormalizer
from app.domain.events.rules.base import RuleEvaluator


class NoopRuleEvaluator(RuleEvaluator):
    def evaluate(self, event: NormalizedEvent) -> List[DerivedEventSpec]:
        return []


class SimpleComponentsFactory(EventComponentsFactory):
    def __init__(self, service: str, schema: Type[BaseModel]):
        self._service = service
        self._schema = schema

    def normalizer(self) -> EventNormalizer:
        return PydanticEventNormalizer(service=self._service, schema=self._schema)

    def rule_evaluator(self) -> RuleEvaluator:
        return NoopRuleEvaluator()
