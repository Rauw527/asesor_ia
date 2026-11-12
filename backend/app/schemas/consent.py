"""Consent request/response contracts."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ConsentCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    consent_type: Literal["service", "training"]  # "service" or "training"
    granted: bool
    version: str = Field(default="1.0", max_length=40)
    purpose: str | None = Field(default=None, max_length=500)


class ConsentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    consent_type: str
    granted: bool
    version: str
    purpose: str | None
    granted_at: datetime | None
    withdrawn_at: datetime | None
    created_at: datetime
