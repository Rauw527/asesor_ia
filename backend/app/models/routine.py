"""Personalized skincare routine (morning / night)."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.types import UTCDateTime, new_id, utcnow

if TYPE_CHECKING:
    from app.models.user import User


class Routine(Base):
    __tablename__ = "routines"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=new_id)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    routine_type: Mapped[str] = mapped_column(String(20))  # "morning" | "night"
    steps: Mapped[list[dict]] = mapped_column(JSON, default=list)
    generated_from: Mapped[str | None] = mapped_column(String(40), default=None)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utcnow)

    user: Mapped[User] = relationship(back_populates="routines")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Routine {self.routine_type} user={self.user_id}>"
