"""Skincare endpoints."""

from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, get_gemini, get_storage
from app.core.config import get_settings
from app.models import User
from app.schemas.skin import SkinAnalysisResponse, SkinProgressResponse
from app.schemas.user import EvolutionHistoryResponse
from app.services import skin_service
from app.services.consent_service import require_service_consent
from app.services.gemini_service import GeminiService
from app.services.image_service import low_light_warning, prepare_image, read_upload
from app.services.storage import LocalStorage

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/skin", tags=["skin"])


@router.post(
    "/analyze",
    response_model=SkinAnalysisResponse,
    summary="Diagnóstico facial cosmético a partir de una selfie",
)
def analyze_skin(
    file: Annotated[UploadFile, File(description="Selfie del rostro (JPEG/PNG/WebP)")],
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    gemini: GeminiService = Depends(get_gemini),
    storage: LocalStorage = Depends(get_storage),
) -> SkinAnalysisResponse:
    config = get_settings()
    require_service_consent(db, user.id)
    if not config.enable_experimental_ai:
        raise HTTPException(503, "El análisis externo está desactivado en esta demo.")
    image = prepare_image(read_upload(file, config), config)

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
    days_elapsed: Annotated[int | None, Form(ge=0, le=3650)] = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    gemini: GeminiService = Depends(get_gemini),
    storage: LocalStorage = Depends(get_storage),
) -> SkinProgressResponse:
    config = get_settings()
    require_service_consent(db, user.id)
    if not config.enable_experimental_ai:
        raise HTTPException(503, "El análisis externo está desactivado en esta demo.")
    baseline = prepare_image(read_upload(baseline_file, config), config)
    current = prepare_image(read_upload(current_file, config), config)

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
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    storage: LocalStorage = Depends(get_storage),
) -> EvolutionHistoryResponse:
    return skin_service.history(db, user=user, storage=storage)
