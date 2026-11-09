"""Pydantic contracts for the skincare module.

These models are the public API surface consumed by the Flutter client and are
also reused as the JSON schema handed to Gemini, so the model cannot drift from
the contract.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

SkinType = Literal["Mixta", "Grasa", "Seca", "Sensible", "Normal"]
Undertone = Literal["Cálido", "Frío", "Neutro"]


class ProductSuggestion(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=2, max_length=120)
    brand: str = Field(min_length=1, max_length=80)
    reason: str = Field(min_length=10, max_length=400)
    affiliate_link: str


class SkinAnalysisResponse(BaseModel):
    """Response of ``POST /api/v1/skin/analyze``."""

    model_config = ConfigDict(str_strip_whitespace=True)

    skin_type: SkinType
    hydration_level: int = Field(ge=0, le=100)
    undertone: Undertone
    detected_issues: list[str] = Field(default_factory=list, max_length=8)
    recommendations: list[str] = Field(default_factory=list, max_length=10)
    product_suggestions: list[ProductSuggestion] = Field(default_factory=list, max_length=5)
    disclaimer: str

    @field_validator("detected_issues", "recommendations")
    @classmethod
    def _clean_list(cls, value: list[str]) -> list[str]:
        return [item.strip() for item in value if item and item.strip()]


class SkinProgressResponse(BaseModel):
    """Response of ``POST /api/v1/skin/compare-progress``."""

    model_config = ConfigDict(str_strip_whitespace=True)

    progress_percentage: int = Field(ge=0, le=100)
    hydration_change: str
    texture_improvement: str
    summary_notes: str
    recommended_routine_adjustments: list[str] = Field(default_factory=list)
