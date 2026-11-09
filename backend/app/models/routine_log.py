"""Daily AM/PM routine check-in."""

from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, Boolean, Date, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.types import UTCDateTime, new_id, utcnow

if TYPE_CHECKING:
    from app.models.user import User


class RoutineLog(Base):
    __tablename__ = "routine_logs"
    __table_args__ = (
        UniqueConstraint("user_id", "log_date", "period", name="uq_routine_day_period"),
    )

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=new_id)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)

    log_date: Mapped[date] = mapped_column(Date(), index=True)
    period: Mapped[str] = mapped_column(String(2))  # "AM" | "PM"
    completed_steps: Mapped[list[str]] = mapped_column(JSON, default=list)
    notes: Mapped[str] = mapped_column(Text(), default="")
    completed: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utcnow, onupdate=utcnow)

    user: Mapped[User] = relationship(back_populates="routine_logs")
