"""Skin analysis contracts."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class AnalysisIn(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    photo_ids: list[str] = Field(default_factory=list)


class AnalysisOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    analysis_status: str
    model_version: str | None
    observations: dict[str, Any]
    confidence: float | None
    limitations: list[str]
    created_at: datetime


class AnalysisResultOut(BaseModel):
    analysis_status: str
    model_version: str | None
    observations: dict[str, Any]
    confidence: float | None
    limitations: list[str]
