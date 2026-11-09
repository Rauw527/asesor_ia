"""Skincare endpoints."""

from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_gemini, get_storage
from app.core.config import get_settings
from app.models import User
from app.repositories import user_repository
from app.schemas.skin import SkinAnalysisResponse, SkinProgressResponse
from app.schemas.user import EvolutionHistoryResponse
from app.services import skin_service
from app.services.gemini_service import GeminiService
from app.services.image_service import low_light_warning, prepare_image
from app.services.storage import LocalStorage

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/skin", tags=["skin"])


def _read_upload(upload: UploadFile) -> bytes:
    upload.file.seek(0)
    return upload.file.read()


@router.post(
    "/analyze",
    response_model=SkinAnalysisResponse,
    summary="Diagnóstico facial cosmético a partir de una selfie",
)
def analyze_skin(
    file: Annotated[UploadFile, File(description="Selfie del rostro (JPEG/PNG/WebP)")],
    user_id: Annotated[
        str | None, Form(description="ID de usuario; usa el demo si se omite")
    ] = None,
    db: Session = Depends(get_db),
    gemini: GeminiService = Depends(get_gemini),
    storage: LocalStorage = Depends(get_storage),
) -> SkinAnalysisResponse:
    config = get_settings()
    user: User = user_repository.resolve_user(db, user_id, config)
    image = prepare_image(_read_upload(file), config)

    warning = low_light_warning(image)
    if warning:
        logger.info("Low-light selfie accepted with warning: %s", warning)

    return skin_service.analyze(
        db, user=user, image=image, gemini=gemini, storage=storage, config=config
    )


@router.post(
    "/compare-progress",
    response_model=SkinProgressResponse,
    summary="Comparativa multimodal Día 1 vs. chequeo actual",
)
def compare_progress(
    baseline_file: Annotated[UploadFile, File(description="Foto de la línea base (semana 1)")],
    current_file: Annotated[UploadFile, File(description="Foto del chequeo actual (semana 4)")],
    user_id: Annotated[
        str | None, Form(description="ID de usuario; usa el demo si se omite")
    ] = None,
    days_elapsed: Annotated[int | None, Form(ge=0, le=3650)] = None,
    db: Session = Depends(get_db),
    gemini: GeminiService = Depends(get_gemini),
    storage: LocalStorage = Depends(get_storage),
) -> SkinProgressResponse:
    config = get_settings()
    user: User = user_repository.resolve_user(db, user_id, config)
    baseline = prepare_image(_read_upload(baseline_file), config)
    current = prepare_image(_read_upload(current_file), config)

    return skin_service.compare_progress(
        db,
        user=user,
        baseline_image=baseline,
        current_image=current,
        days_elapsed=days_elapsed,
        gemini=gemini,
        storage=storage,
        config=config,
    )


@router.get(
    "/history",
    response_model=EvolutionHistoryResponse,
    summary="Historial de chequeos con URL de cada imagen",
)
def evolution_history(
    user_id: str | None = None,
    db: Session = Depends(get_db),
    storage: LocalStorage = Depends(get_storage),
) -> EvolutionHistoryResponse:
    config = get_settings()
    user = user_repository.resolve_user(db, user_id, config)
    return skin_service.history(db, user=user, storage=storage)
