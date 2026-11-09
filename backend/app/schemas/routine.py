"""Routine contracts (original Phase 1 + Fase 3 recommendations)."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict, Field


# --- Original Phase 1 routine schemas (expected by app/schemas/__init__.py) ---

ROUTINE_STEPS: list[str] = ["cleansing", "moisturizing", "sunscreen", "treatment"]


class RoutineCheckinRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    date: str
    period: str = Field(pattern="^(AM|PM)$")
    completed_steps: list[str] = Field(default_factory=list)
    notes: str | None = None


class RoutineCheckinResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    log_date: str
    period: str
    completed_steps: list[str]
    notes: str | None
    completed: bool


class RoutineDayResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    date: str
    morning: RoutineCheckinResponse | None = None
    night: RoutineCheckinResponse | None = None


class RoutineLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    log_date: str
    period: str
    completed_steps: list[str]
    notes: str | None
    completed: bool
    created_at: datetime


# --- Fase 3 recommendation schemas ---

class RoutineStepOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    order: int
    step: str
    title: str
    explanation: str
    suggested_products: list[Any] = []


class RoutineOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    routine_type: str
    steps: list[dict[str, Any]]
    generated_from: str | None
    created_at: datetime
