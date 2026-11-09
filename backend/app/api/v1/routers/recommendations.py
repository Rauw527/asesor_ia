"""Skin recommendation endpoints (morning / night routines)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.routine import RoutineOut
from app.services.recommendation_service import (
    generate_routine,
    get_routine,
    list_user_routines,
)
from sqlalchemy.orm import Session

router = APIRouter(tags=["recommendations"])


@router.post(
    "/recommendations",
    response_model=RoutineOut,
    status_code=status.HTTP_201_CREATED,
    summary="Generate a morning or night routine",
)
def create_recommendation(
    routine_type: str = Query(..., description="'morning' or 'night'"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RoutineOut:
    if routine_type not in ("morning", "night"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="routine_type must be 'morning' or 'night'",
        )
    from app.services.skin_profile_service import get_user_assessment

    assessment = get_user_assessment(db, current_user.id)
    routine = generate_routine(db, current_user.id, routine_type, assessment)
    return RoutineOut.model_validate(routine)


@router.get(
    "/recommendations",
    response_model=list[RoutineOut],
    summary="List user's routines",
)
def list_recommendations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[RoutineOut]:
    return [RoutineOut.model_validate(r) for r in list_user_routines(db, current_user.id)]


@router.get(
    "/recommendations/{routine_id}",
    response_model=RoutineOut,
    summary="Get a specific routine",
)
def get_recommendation(
    routine_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RoutineOut:
    routine = get_routine(db, routine_id, current_user.id)
    if not routine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rutina no encontrada",
        )
    return RoutineOut.model_validate(routine)
