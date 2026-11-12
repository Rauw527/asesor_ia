"""User face photos (private storage)."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.types import UTCDateTime, new_id, utcnow

if TYPE_CHECKING:
    from app.models.user import User


class Photo(Base):
    __tablename__ = "photos"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=new_id)
    user_id: Mapped[str] = mapped_column(String(32), ForeignKey("users.id"), index=True)
    photo_type: Mapped[str] = mapped_column(
        String(20), index=True
    )  # "frontal", "left_cheek", "right_cheek"
    storage_path: Mapped[str] = mapped_column(String(500))
    original_filename: Mapped[str | None] = mapped_column(String(255), default=None)
    content_type: Mapped[str] = mapped_column(String(60), default="image/jpeg")
    size_bytes: Mapped[int] = mapped_column(default=0)
    consent_version: Mapped[str | None] = mapped_column(String(40), default=None)
    uploaded_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utcnow)

    user: Mapped[User] = relationship(back_populates="photos")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Photo {self.photo_type} user={self.user_id}>"
