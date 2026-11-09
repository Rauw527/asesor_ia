"""Persistent cosmetic profile of a user (Phase 1 + Phase 2 slots)."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.types import UTCDateTime, new_id, utcnow

if TYPE_CHECKING:
    from app.models.user import User


class SkinProfile(Base):
    __tablename__ = "skin_profiles"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=new_id)
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True
    )

    # --- Module 1: skincare (populated by POST /skin/analyze)
    skin_type: Mapped[str | None] = mapped_column(String(32))
    hydration_level: Mapped[int | None] = mapped_column(Integer)
    undertone: Mapped[str | None] = mapped_column(String(32))
    detected_issues: Mapped[list[str]] = mapped_column(JSON, default=list)
    recommendations: Mapped[list[str]] = mapped_column(JSON, default=list)
    last_analyzed_at: Mapped[datetime | None] = mapped_column(UTCDateTime())

    # --- Module 2 slots: outfit & style (prepared, intentionally unused)
    colorimetry_season: Mapped[str | None] = mapped_column(String(32))
    body_shape: Mapped[str | None] = mapped_column(String(32))
    style_preference: Mapped[str | None] = mapped_column(String(64))

    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utcnow, onupdate=utcnow)

    user: Mapped[User] = relationship(back_populates="skin_profile")
