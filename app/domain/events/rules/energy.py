from __future__ import annotations

from typing import List

from app.domain.events.rules.base import RuleEvaluator
from app.domain.events.types import DerivedEventSpec, NormalizedEvent


class EnergyRuleEvaluator(RuleEvaluator):
    THRESHOLD_KWH: float = 500.0

    def evaluate(self, normalized_event: NormalizedEvent) -> List[DerivedEventSpec]:
        p = normalized_event.normalized_payload
        energy = p.get("energy")

        if energy is None or energy <= self.THRESHOLD_KWH:
            return []
        
        return [
            DerivedEventSpec(
                service="security",
                payload={
                    "alert": "possible_risk",
                    "reason": "critical_energy_usage",
                    "neighborhood": p.get("neighborhood"),
                    "energy": energy,
                },
                deduplication_key=f"critical_energy_usage_{p.get('neighborhood')}"
            )
        ]