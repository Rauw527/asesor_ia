"""Ingredient contracts."""

from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, ConfigDict


class IngredientOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    inci_name: str
    common_name: str | None
    function: str | None
    description: str | None
    precautions: str | None
    evidence_level: str | None
    sources: str | None
    created_at: datetime
