"""Monthly evolution log: one row per captured check-in photo."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.types import UTCDateTime, new_id, utcnow

if TYPE_CHECKING:
    from app.models.user import User


class SkinEvolutionLog(Base):
    __tablename__ = "skin_evolution_logs"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=new_id)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)

    captured_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utcnow, index=True)
    week_number: Mapped[int] = mapped_column(Integer, default=1)
    is_baseline: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relative storage path (served through /api/v1/media/...).
    image_path: Mapped[str] = mapped_column(String(255))

    skin_type: Mapped[str | None] = mapped_column(String(32))
    hydration_level: Mapped[int | None] = mapped_column(Integer)
    undertone: Mapped[str | None] = mapped_column(String(32))
    detected_issues: Mapped[list[str]] = mapped_column(JSON, default=list)

    # Filled by POST /skin/compare-progress when this row is the "current" photo.
    progress_percentage: Mapped[int | None] = mapped_column(Integer)
    summary_notes: Mapped[str] = mapped_column(Text(), default="")

    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utcnow)

    user: Mapped[User] = relationship(back_populates="evolution_logs")
