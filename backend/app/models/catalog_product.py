"""Cosmetic product catalog (reference data, may include demo/fictitious items)."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, Boolean, String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.types import UTCDateTime, new_id, utcnow

if TYPE_CHECKING:
    from app.models.ingredient import Ingredient


class CatalogProduct(Base):
    __tablename__ = "catalog_products"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=new_id)
    name: Mapped[str] = mapped_column(String(160))
    brand: Mapped[str] = mapped_column(String(120), default="")
    category: Mapped[str | None] = mapped_column(String(80), default=None)
    description: Mapped[str | None] = mapped_column(Text, default=None)
    inci_list: Mapped[list[str]] = mapped_column(JSON, default=list)
    active_ingredients: Mapped[list[str]] = mapped_column(JSON, default=list)
    function: Mapped[str | None] = mapped_column(String(160), default=None)
    concentration_declared: Mapped[str | None] = mapped_column(String(160), default=None)
    warnings: Mapped[str | None] = mapped_column(Text, default=None)
    price_guide: Mapped[str | None] = mapped_column(String(80), default=None)
    image_url: Mapped[str | None] = mapped_column(String(500), default=None)
    availability: Mapped[str | None] = mapped_column(String(80), default=None)
    is_demo_data: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utcnow)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<CatalogProduct {self.name}>"
