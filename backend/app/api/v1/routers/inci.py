"""INCI scanner endpoint."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_cache, get_current_user, get_db, get_gemini, get_storage
from app.core.config import get_settings
from app.models import User
from app.schemas.inci import INCIScanResponse
from app.services import inci_service
from app.services.cache import CacheBackend
from app.services.consent_service import require_service_consent
from app.services.gemini_service import GeminiService
from app.services.image_service import prepare_image, read_upload
from app.services.storage import LocalStorage

router = APIRouter(prefix="/inci", tags=["inci"])


@router.post(
    "/scan",
    response_model=INCIScanResponse,
    summary="Lectura de etiqueta INCI y auditoría de compatibilidad",
)
def scan_inci(
    file: Annotated[UploadFile, File(description="Foto de la lista INCI del envase")],
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    gemini: GeminiService = Depends(get_gemini),
    cache: CacheBackend = Depends(get_cache),
    storage: LocalStorage = Depends(get_storage),
) -> INCIScanResponse:
    config = get_settings()
    require_service_consent(db, user.id)
    if not config.enable_experimental_ai:
        raise HTTPException(503, "El análisis externo está desactivado en esta demo.")

    file.file.seek(0)
    image = prepare_image(read_upload(file, config), config)

    return inci_service.scan(
        db,
        user=user,
        image=image,
        gemini=gemini,
        cache=cache,
        storage=storage,
        config=config,
    )
