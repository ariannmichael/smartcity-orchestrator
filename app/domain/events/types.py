from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class NormalizedEvent:
    service: str
    timestamp: datetime
    raw_payload: Dict[str, Any]
    normalized_payload: Dict[str, Any]


@dataclass
class DerivedEventSpec:
    service: str
    payload: Dict[str, Any]
    deduplication_key: Optional[str] = None
