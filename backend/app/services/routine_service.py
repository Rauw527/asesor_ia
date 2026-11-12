"""Daily routine use cases."""

from __future__ import annotations

from datetime import date

from sqlalchemy.orm import Session

from app.core.exceptions import DomainValidationError
from app.models import User
from app.repositories import routine_log_repository as routine_repository
from app.schemas.routine import (
    ROUTINE_STEPS,
    RoutineCheckinRequest,
    RoutineCheckinResponse,
    RoutineDayResponse,
    RoutineLogOut,
)


def checkin(db: Session, *, user: User, payload: RoutineCheckinRequest) -> RoutineCheckinResponse:
    allowed = ROUTINE_STEPS[payload.period]
    unknown = [step for step in payload.completed_steps if step not in allowed]
    if unknown:
        raise DomainValidationError(
            f"Pasos no válidos para {payload.period}: {', '.join(unknown)}. "
            f"Permitidos: {', '.join(allowed)}."
        )

    completed = set(payload.completed_steps) == set(allowed)

    log = routine_repository.upsert_log(
        db,
        user_id=user.id,
        log_date=payload.log_date,
        period=payload.period,
        completed_steps=payload.completed_steps,
        notes=payload.notes,
        completed=completed,
    )
    db.commit()
    return RoutineCheckinResponse(log=RoutineLogOut.model_validate(log))


def day(db: Session, *, user: User, on_date: date) -> RoutineDayResponse:
    am, pm = routine_repository.get_day(db, user.id, on_date)
    return RoutineDayResponse(
        log_date=on_date,
        am=RoutineLogOut.model_validate(am) if am else None,
        pm=RoutineLogOut.model_validate(pm) if pm else None,
        allowed_steps=ROUTINE_STEPS,
        streak_days=routine_repository.streak_days(db, user.id, on_date),
    )
