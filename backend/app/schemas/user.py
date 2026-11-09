"""Pydantic contracts for users and the evolution history."""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class SkinProfileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    skin_type: str | None = None
    hydration_level: int | None = None
    undertone: str | None = None
    detected_issues: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    last_analyzed_at: datetime | None = None
    colorimetry_season: str | None = None
    body_shape: str | None = None
    style_preference: str | None = None


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    full_name: str
    onboarding_completed: bool
    skin_profile: SkinProfileOut | None = None


class EvolutionLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    captured_at: datetime
    week_number: int
    is_baseline: bool
    skin_type: str | None = None
    hydration_level: int | None = None
    undertone: str | None = None
    detected_issues: list[str] = Field(default_factory=list)
    progress_percentage: int | None = None
    summary_notes: str = ""
    image_url: str = ""


class EvolutionHistoryResponse(BaseModel):
    items: list[EvolutionLogOut] = Field(default_factory=list)


class DaySummary(BaseModel):
    log_date: date
    am_completed: bool = False
    pm_completed: bool = False
