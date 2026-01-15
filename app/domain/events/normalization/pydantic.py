from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Type

from pydantic import BaseModel, ValidationError

from app.domain.events.normalization.base import EventNormalizer
from app.domain.events.types import NormalizedEvent


class PydanticEventNormalizer(EventNormalizer):
    def __init__(self, service: str, schema: Type[BaseModel]):
        self._service = service
        self._schema = schema

    def normalize(self, raw_payload: Dict[str, Any]) -> NormalizedEvent:
        try:
            parsed = self._schema.model_validate(raw_payload)
            normalized = parsed.model_dump()
        except ValidationError:
            normalized = dict(raw_payload)

        return NormalizedEvent(
            service=self._service,
            timestamp=datetime.now(),
            raw_payload=raw_payload,
            normalized_payload=normalized,
        )
