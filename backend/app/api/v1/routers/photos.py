"""Photo upload endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, UploadFile, status

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.photo import PhotoOut, PhotoUploadResponse
from app.services.photo_service import list_user_photos, save_uploaded_file
from sqlalchemy.orm import Session

router = APIRouter(tags=["photos"])


@router.post(
    "/photos",
    response_model=PhotoUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Subir una foto del rostro",
)
def upload_photo(
    photo_type: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PhotoUploadResponse:
    return save_uploaded_file(db, current_user.id, photo_type, file)


@router.get("/photos", response_model=list[PhotoOut], summary="Mis fotos")
def list_photos_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[PhotoOut]:
    return list_user_photos(db, current_user.id)
