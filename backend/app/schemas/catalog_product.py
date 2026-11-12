"""Catalog product contracts."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CatalogProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    brand: str
    category: str | None
    description: str | None
    inci_list: list[str]
    active_ingredients: list[str]
    function: str | None
    concentration_declared: str | None
    warnings: str | None
    price_guide: str | None
    image_url: str | None
    availability: str | None
    is_demo_data: bool
    created_at: datetime


class ProductSuggestionOut(BaseModel):
    id: str
    name: str
    brand: str
    function: str | None
    warnings: str | None
    is_demo_data: bool
