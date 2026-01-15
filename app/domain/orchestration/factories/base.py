from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.events.normalization.base import EventNormalizer
from app.domain.events.rules.base import RuleEvaluator


class EventComponentsFactory(ABC):
    @abstractmethod
    def normalizer(self) -> EventNormalizer:
        raise NotImplementedError

    @abstractmethod
    def rule_evaluator(self) -> RuleEvaluator:
        raise NotImplementedError
