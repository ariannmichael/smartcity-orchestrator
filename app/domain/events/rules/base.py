from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from app.domain.events.types import DerivedEventSpec, NormalizedEvent


class RuleEvaluator(ABC):
    @abstractmethod
    def evaluate(self, normalized_event: NormalizedEvent) -> List[DerivedEventSpec]:
        raise NotImplementedError
