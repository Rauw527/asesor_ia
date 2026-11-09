"""Photo upload business logic."""

from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import HTTPException, status, UploadFile

from app.core.config import get_settings
from app.repositories import photo_repository
from app.schemas.photo import PhotoOut, PhotoUploadResponse

settings = get_settings()

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}


def save_uploaded_file(db, user_id: str, photo_type: str, file: UploadFile) -> PhotoUploadResponse:
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tipo de archivo no permitido. Usa JPEG, PNG o WEBP.",
        )

    content = file.file.read()
    size_mb = len(content) / (1024 * 1024)
    if size_mb > settings.max_upload_mb:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Archivo demasiado grande (máx. {settings.max_upload_mb} MB).",
        )

    storage_dir = Path(settings.storage_dir)
    storage_dir.mkdir(parents=True, exist_ok=True)

    ext = Path(file.filename or "").suffix or ".jpg"
    filename = f"{user_id}/{photo_type}/{uuid.uuid4().hex}{ext}"
    disk_path = storage_dir / filename
    disk_path.parent.mkdir(parents=True, exist_ok=True)
    disk_path.write_bytes(content)

    # Consent version: require service consent (A) to store photos
    from app.repositories import consent_repository

    consent = consent_repository.get_consent(db, user_id, "service")
    consent_version = consent.version if consent else None

    photo = photo_repository.save_photo(
        db,
        user_id=user_id,
        photo_type=photo_type,
        storage_path=str(disk_path),
        original_filename=file.filename,
        content_type=file.content_type or "image/jpeg",
        size_bytes=len(content),
        consent_version=consent_version,
    )
    db.commit()

    return PhotoUploadResponse(
        photo_id=photo.id,
        photo_type=photo.photo_type,
        message="Foto guardada correctamente",
    )


def list_user_photos(db, user_id: str) -> list[PhotoOut]:
    photos = photo_repository.list_photos(db, user_id)
    return [PhotoOut.model_validate(p) for p in photos]
