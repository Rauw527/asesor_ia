"""Orientative skin profile combining questionnaire + visual analysis + history."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.types import UTCDateTime, new_id, utcnow

if TYPE_CHECKING:
    from app.models.user import User


class SkinAssessment(Base):
    __tablename__ = "skin_assessments"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=new_id)
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True
    )
    perceived_skin_type: Mapped[str | None] = mapped_column(String(32), default=None)
    sensitivity: Mapped[str | None] = mapped_column(String(32), default=None)
    main_concerns: Mapped[list[str]] = mapped_column(JSON, default=list)
    questionnaire_completed: Mapped[bool] = mapped_column(default=False)
    visual_analysis_status: Mapped[str] = mapped_column(String(20), default="demo")
    data_source: Mapped[str] = mapped_column(
        String(40), default="questionnaire"
    )  # "questionnaire" | "visual" | "mixed"
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        UTCDateTime(), default=utcnow, onupdate=utcnow
    )

    user: Mapped["User"] = relationship(back_populates="skin_assessments")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<SkinAssessment user={self.user_id} type={self.perceived_skin_type}>"
