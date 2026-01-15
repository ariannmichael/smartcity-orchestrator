from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict

from app.domain.events.types import NormalizedEvent


class EventNormalizer(ABC):
    @abstractmethod
    def normalize(self, raw_payload: Dict[str, Any]) -> NormalizedEvent:
        raise NotImplementedError
