"""Photo upload endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, HTTPException, Response, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.repositories import photo_repository
from app.schemas.photo import PhotoOut, PhotoUploadResponse
from app.services.photo_service import (
    delete_photo,
    list_user_photos,
    private_path,
    save_uploaded_file,
)

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


@router.get("/photos/{photo_id}/content", summary="Mi fotografía privada")
def photo_content(
    photo_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    photo = photo_repository.get_photo(db, photo_id, current_user.id)
    if photo is None:
        raise HTTPException(404, "Fotografía no encontrada")
    path = private_path(photo.storage_path)
    if not path.is_file():
        raise HTTPException(404, "Fotografía no encontrada")
    return FileResponse(
        path,
        media_type="image/jpeg",
        headers={"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff"},
    )


@router.delete("/photos/{photo_id}", status_code=204)
def remove_photo(
    photo_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    delete_photo(db, current_user.id, photo_id)
    return Response(status_code=204)
