from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict


class BasePayload(BaseModel):
    model_config = ConfigDict(extra="allow")


class HealthPayload(BasePayload):
    patient_id: Optional[int] = None
    alert: Optional[str] = None
    location: Optional[str] = None


class EnergyPayload(BasePayload):
    energy: Optional[float] = None
    neighborhood: Optional[str] = None


class TransportPayload(BasePayload):
    bus_id: Optional[int] = None
    lat: Optional[float] = None
    lon: Optional[float] = None


class SecurityPayload(BasePayload):
    alert: Optional[bool] = None
    camera_trigger: Optional[str] = None
