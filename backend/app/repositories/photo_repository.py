"""Photo persistence helpers."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.photo import Photo


def save_photo(
    db: Session,
    user_id: str,
    photo_type: str,
    storage_path: str,
    original_filename: str | None = None,
    content_type: str = "image/jpeg",
    size_bytes: int = 0,
    consent_version: str | None = None,
) -> Photo:
    photo = Photo(
        user_id=user_id,
        photo_type=photo_type,
        storage_path=storage_path,
        original_filename=original_filename,
        content_type=content_type,
        size_bytes=size_bytes,
        consent_version=consent_version,
    )
    db.add(photo)
    db.flush()
    return photo


def list_photos(db: Session, user_id: str) -> list[Photo]:
    return list(db.execute(select(Photo).where(Photo.user_id == user_id)).scalars())


def get_photo(db: Session, photo_id: str, user_id: str) -> Photo | None:
    return db.execute(
        select(Photo).where(Photo.id == photo_id, Photo.user_id == user_id)
    ).scalar_one_or_none()
