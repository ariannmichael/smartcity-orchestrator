from __future__ import annotations

from typing import List

from app.domain.events.rules.base import RuleEvaluator
from app.domain.events.types import DerivedEventSpec, NormalizedEvent


class EnergyRuleEvaluator(RuleEvaluator):
    def evaluate(self, normalized_event: NormalizedEvent) -> List[DerivedEventSpec]:
        return []
