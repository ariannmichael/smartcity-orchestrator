from __future__ import annotations

from typing import List

from app.domain.events.rules.base import RuleEvaluator
from app.domain.events.types import DerivedEventSpec, NormalizedEvent


class HealthRuleEvaluator(RuleEvaluator):
    def evaluate(self, normalized_event: NormalizedEvent) -> List[DerivedEventSpec]:
        p = normalized_event.normalized_payload
        if p.get("alert") != "emergency":
            return []
        
        return [
            DerivedEventSpec(
                service="transport",
                payload={
                    "action": "dispatch_nearest_vehicle",
                    "reason": "health_emergency",
                    "location": p.get("location"),
                    "patient_id": p.get("patient_id"),
                },
                deduplication_key=f"health_emergency_{p.get('patient_id')}"
            ),
            DerivedEventSpec(
                service="security",
                payload={
                    "priority": "high",
                    "action": "escort_and_clear_traffic",
                    "reason": "health_emergency",
                    "location": p.get("location"),
                    "patient_id": p.get("patient_id"),
                },
                deduplication_key=f"health_emergency_{p.get('patient_id')}"
            ),
        ]
