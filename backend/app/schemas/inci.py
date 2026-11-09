"""Pydantic contracts for the INCI scanner."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SafeAlternative(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=2, max_length=160)
    reason: str = Field(min_length=10, max_length=400)
    affiliate_link: str


class INCIScanResponse(BaseModel):
    """Response of ``POST /api/v1/inci/scan``."""

    model_config = ConfigDict(str_strip_whitespace=True)

    product_name: str
    key_ingredients: list[str] = Field(default_factory=list)
    has_conflict: bool
    conflict_warning: str | None = None
    safe_alternative: SafeAlternative | None = None

    @field_validator("key_ingredients")
    @classmethod
    def _clean_ingredients(cls, value: list[str]) -> list[str]:
        seen: set[str] = set()
        cleaned: list[str] = []
        for item in value:
            normalized = item.strip()
            key = normalized.casefold()
            if normalized and key not in seen:
                seen.add(key)
                cleaned.append(normalized)
        return cleaned
