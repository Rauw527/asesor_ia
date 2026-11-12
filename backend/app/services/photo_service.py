"""Private photo storage; authorization and decoding precede every write."""

import uuid
from pathlib import Path

from fastapi import HTTPException

from app.core.config import get_settings
from app.repositories import photo_repository
from app.schemas.photo import PhotoOut, PhotoUploadResponse
from app.services.consent_service import require_service_consent
from app.services.image_service import prepare_image, read_upload

PHOTO_TYPES = {"front", "left", "right", "frontal", "left_cheek", "right_cheek"}


def private_path(relative_path):
    root = get_settings().storage_dir.resolve()
    candidate = (root / relative_path).resolve()
    if not candidate.is_relative_to(root) or candidate == root:
        raise HTTPException(404, "Fotografía no encontrada")
    return candidate


def save_uploaded_file(db, user_id, photo_type, file):
    consent = require_service_consent(db, user_id)
    if photo_type not in PHOTO_TYPES:
        raise HTTPException(422, "Tipo de foto no válido")
    image = prepare_image(read_upload(file, get_settings()), get_settings())
    relative = f"photos/{user_id}/{uuid.uuid4().hex}.jpg"
    path = private_path(relative)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(image.data)
    try:
        photo = photo_repository.save_photo(
            db,
            user_id=user_id,
            photo_type=photo_type,
            storage_path=relative,
            original_filename=Path(file.filename or "foto.jpg").name[:255],
            content_type="image/jpeg",
            size_bytes=len(image.data),
            consent_version=consent.version,
        )
        db.commit()
    except Exception:
        db.rollback()
        path.unlink(missing_ok=True)
        raise
    return PhotoUploadResponse(
        photo_id=photo.id,
        photo_type=photo.photo_type,
        message="Foto privada guardada. No se ha enviado a un proveedor de IA.",
    )


def list_user_photos(db, user_id):
    return [PhotoOut.model_validate(p) for p in photo_repository.list_photos(db, user_id)]


def delete_photo(db, user_id, photo_id):
    photo = photo_repository.get_photo(db, photo_id, user_id)
    if photo is None:
        raise HTTPException(404, "Fotografía no encontrada")
    private_path(photo.storage_path).unlink(missing_ok=True)
    db.delete(photo)
    db.commit()
