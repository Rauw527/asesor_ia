"""Reference dictionary of cosmetic ingredients and their known conflicts."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base
from app.models.types import EmbeddingType, UTCDateTime, new_id, utcnow


class INCIIngredient(Base):
    __tablename__ = "inci_ingredients"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=new_id)
    inci_name: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(160))
    category: Mapped[str] = mapped_column(String(48), index=True)
    aliases: Mapped[list[str]] = mapped_column(JSON, default=list)
    conflicts_with: Mapped[list[str]] = mapped_column(JSON, default=list)
    risk_notes: Mapped[str | None] = mapped_column(Text())

    # Phase 2: semantic matching against free-text INCI labels.
    embedding: Mapped[list[float] | None] = mapped_column(EmbeddingType(), nullable=True)

    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utcnow)
