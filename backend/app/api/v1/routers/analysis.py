"""Skin visual analysis endpoints (demo provider by default)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.skin_analysis import AnalysisIn, AnalysisOut, AnalysisResultOut
from app.services.skin_analysis_service import (
    get_analysis,
    list_user_analyses,
    run_analysis,
)

router = APIRouter(tags=["skin-analysis"])


@router.post(
    "/analysis",
    response_model=AnalysisResultOut,
    status_code=status.HTTP_201_CREATED,
    summary="Run skin visual analysis (demo provider)",
)
async def analyze_skin(
    payload: AnalysisIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AnalysisResultOut:
    # In MVP we don't store actual photo paths; photo_ids are enough.
    # The demo provider does not need real images.
    from app.repositories.photo_repository import get_photo
    from app.services.consent_service import require_service_consent

    require_service_consent(db, current_user.id)
    if not payload.photo_ids or any(
        get_photo(db, photo_id, current_user.id) is None for photo_id in payload.photo_ids
    ):
        raise HTTPException(404, "Fotografías no encontradas")
    analysis = await run_analysis(
        db,
        user_id=current_user.id,
        photo_ids=payload.photo_ids,
        photo_paths=[],
    )
    return AnalysisResultOut(
        analysis_status=analysis.analysis_status,
        model_version=analysis.model_version,
        observations=analysis.observations,
        confidence=analysis.confidence,
        limitations=analysis.limitations,
    )


@router.get(
    "/analysis/records/{analysis_id}",
    response_model=AnalysisOut,
    summary="Get a past skin analysis",
)
def get_analysis_endpoint(
    analysis_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AnalysisOut:
    analysis = get_analysis(db, analysis_id, current_user.id)
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Análisis no encontrado",
        )
    return AnalysisOut.model_validate(analysis)


@router.get(
    "/analysis/history",
    response_model=list[AnalysisOut],
    summary="List user's skin analyses",
)
def list_analyses_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[AnalysisOut]:
    return [AnalysisOut.model_validate(a) for a in list_user_analyses(db, current_user.id)]
