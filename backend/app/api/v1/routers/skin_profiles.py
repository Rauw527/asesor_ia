"""Skin assessment (orientative profile) endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.skin_assessment import SkinAssessmentOut
from app.services.skin_profile_service import build_assessment, get_user_assessment
from sqlalchemy.orm import Session

router = APIRouter(tags=["skin-profile"])


@router.get(
    "/skin-profile",
    response_model=SkinAssessmentOut | None,
    summary="Get orientative skin profile",
)
def get_skin_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SkinAssessmentOut | None:
    return get_user_assessment(db, current_user.id)


@router.post(
    "/skin-profile/build",
    response_model=SkinAssessmentOut,
    summary="Build or rebuild orientative skin profile",
)
def build_skin_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SkinAssessmentOut:
    assessment = build_assessment(db, current_user.id)
    return SkinAssessmentOut.model_validate(assessment)
