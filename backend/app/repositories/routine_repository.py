"""Routine persistence helpers."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.routine import Routine


def save_routine(
    db: Session,
    user_id: str,
    routine_type: str,
    steps: list[dict],
    generated_from: str | None = None,
) -> Routine:
    routine = Routine(
        user_id=user_id,
        routine_type=routine_type,
        steps=steps,
        generated_from=generated_from,
    )
    db.add(routine)
    db.flush()
    return routine


def list_routines(db: Session, user_id: str) -> list[Routine]:
    return list(
        db.execute(
            select(Routine)
            .where(Routine.user_id == user_id)
            .order_by(Routine.created_at.desc())
        ).scalars()
    )


def get_routine(db: Session, routine_id: str, user_id: str) -> Routine | None:
    return db.execute(
        select(Routine).where(Routine.id == routine_id, Routine.user_id == user_id)
    ).scalar_one_or_none()
