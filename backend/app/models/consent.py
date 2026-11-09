"""Consent records for photos and AI training."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.types import UTCDateTime, new_id, utcnow

if TYPE_CHECKING:
    from app.models.user import User


class Consent(Base):
    __tablename__ = "consents"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=new_id)
    user_id: Mapped[str] = mapped_column(String(32), ForeignKey("users.id"), index=True)
    consent_type: Mapped[str] = mapped_column(
        String(20), index=True
    )  # "service" (A) or "training" (B)
    granted: Mapped[bool] = mapped_column(Boolean, default=False)
    version: Mapped[str] = mapped_column(String(40), default="1.0")
    purpose: Mapped[str | None] = mapped_column(Text, default=None)
    granted_at: Mapped[datetime | None] = mapped_column(UTCDateTime(), default=None)
    withdrawn_at: Mapped[datetime | None] = mapped_column(UTCDateTime(), default=None)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        UTCDateTime(), default=utcnow, onupdate=utcnow
    )

    user: Mapped["User"] = relationship(back_populates="consents")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Consent {self.consent_type} granted={self.granted} user={self.user_id}>"
