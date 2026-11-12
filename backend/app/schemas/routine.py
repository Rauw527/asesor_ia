"""Separate daily check-ins from generated routine plans."""

from datetime import date, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

ROUTINE_STEPS = {
    "AM": ["limpiador", "hidratante", "protector_solar"],
    "PM": ["limpiador", "hidratante"],
}


class RoutineCheckinRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    log_date: date = Field(default_factory=date.today)
    period: Literal["AM", "PM"]
    completed_steps: list[str] = Field(default_factory=list, max_length=20)
    notes: str = Field(default="", max_length=2000)
    completed: bool | None = None


class RoutineLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    log_date: date
    period: str
    completed_steps: list[str]
    notes: str
    completed: bool
    created_at: datetime


class RoutineCheckinResponse(BaseModel):
    status: str = "saved"
    log: RoutineLogOut


class RoutineDayResponse(BaseModel):
    log_date: date
    am: RoutineLogOut | None = None
    pm: RoutineLogOut | None = None
    allowed_steps: dict[str, list[str]]
    streak_days: int = 0


class RoutineStepOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    order: int
    step: str
    title: str
    explanation: str
    suggested_products: list[Any] = Field(default_factory=list)


class RoutineOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    routine_type: str
    steps: list[dict[str, Any]]
    generated_from: str | None
    created_at: datetime
