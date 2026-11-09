"""Cosmetic ingredient catalog (INCI)."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base
from app.models.types import UTCDateTime, new_id, utcnow


class Ingredient(Base):
    __tablename__ = "ingredients"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=new_id)
    inci_name: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    common_name: Mapped[str | None] = mapped_column(String(160), default=None)
    function: Mapped[str | None] = mapped_column(String(160), default=None)
    description: Mapped[str | None] = mapped_column(Text, default=None)
    precautions: Mapped[str | None] = mapped_column(Text, default=None)
    evidence_level: Mapped[str | None] = mapped_column(String(40), default=None)
    sources: Mapped[str | None] = mapped_column(Text, default=None)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utcnow)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Ingredient {self.inci_name}>"
