"""INCI scanner endpoint."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_cache, get_db, get_gemini, get_storage
from app.core.config import get_settings
from app.repositories import user_repository
from app.schemas.inci import INCIScanResponse
from app.services import inci_service
from app.services.cache import CacheBackend
from app.services.gemini_service import GeminiService
from app.services.image_service import prepare_image
from app.services.storage import LocalStorage

router = APIRouter(prefix="/inci", tags=["inci"])


@router.post(
    "/scan",
    response_model=INCIScanResponse,
    summary="Lectura de etiqueta INCI y auditoría de compatibilidad",
)
def scan_inci(
    file: Annotated[UploadFile, File(description="Foto de la lista INCI del envase")],
    user_id: Annotated[
        str | None, Form(description="ID de usuario; usa el demo si se omite")
    ] = None,
    db: Session = Depends(get_db),
    gemini: GeminiService = Depends(get_gemini),
    cache: CacheBackend = Depends(get_cache),
    storage: LocalStorage = Depends(get_storage),
) -> INCIScanResponse:
    config = get_settings()
    user = user_repository.resolve_user(db, user_id, config)

    file.file.seek(0)
    image = prepare_image(file.file.read(), config)

    return inci_service.scan(
        db,
        user=user,
        image=image,
        gemini=gemini,
        cache=cache,
        storage=storage,
        config=config,
    )
