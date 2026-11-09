"""Daily routine tracker endpoints."""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.config import get_settings
from app.repositories import user_repository
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
    payload: RoutineCheckinRequest, db: Session = Depends(get_db)
) -> RoutineCheckinResponse:
    user = user_repository.resolve_user(db, payload.user_id, get_settings())
    return routine_service.checkin(db, user=user, payload=payload)


@router.get(
    "/today",
    response_model=RoutineDayResponse,
    summary="Estado del día, pasos permitidos y racha",
)
def today(
    user_id: str | None = None,
    on_date: date | None = Query(default=None, alias="date"),
    db: Session = Depends(get_db),
) -> RoutineDayResponse:
    user = user_repository.resolve_user(db, user_id, get_settings())
    return routine_service.day(db, user=user, on_date=on_date or date.today())
