"""Skin visual analysis records (demo or real model)."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.types import UTCDateTime, new_id, utcnow

if TYPE_CHECKING:
    from app.models.user import User


class SkinAnalysis(Base):
    __tablename__ = "skin_analyses"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=new_id)
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    photo_ids: Mapped[list[str]] = mapped_column(JSON, default=list)
    analysis_status: Mapped[str] = mapped_column(String(20), default="demo")  # "demo" | "real"
    model_version: Mapped[str | None] = mapped_column(String(64), default=None)
    observations: Mapped[dict] = mapped_column(JSON, default=dict)
    confidence: Mapped[float | None] = mapped_column(default=None)
    limitations: Mapped[list[str]] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utcnow)

    user: Mapped["User"] = relationship(back_populates="skin_analyses")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<SkinAnalysis {self.analysis_status} user={self.user_id}>"
