"""Daily routine tracker endpoints."""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.routine import (
    RoutineCheckinRequest,
    RoutineCheckinResponse,
    RoutineDayResponse,
)
from app.services import routine_service

router = APIRouter(prefix="/routine", tags=["routine"])


@router.post(
    "/checkin",
    response_model=RoutineCheckinResponse,
    summary="Registra el checklist AM o PM del día",
)
def checkin(
    payload: RoutineCheckinRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> RoutineCheckinResponse:
    return routine_service.checkin(db, user=user, payload=payload)


@router.get(
    "/today",
    response_model=RoutineDayResponse,
    summary="Estado del día, pasos permitidos y racha",
)
def today(
    user: User = Depends(get_current_user),
    on_date: date | None = Query(default=None, alias="date"),
    db: Session = Depends(get_db),
) -> RoutineDayResponse:
    return routine_service.day(db, user=user, on_date=on_date or date.today())
