"""Persistence for daily adherence, independent of recommended plans."""

from datetime import timedelta

from sqlalchemy import select

from app.models.routine_log import RoutineLog


def upsert_log(db, *, user_id, log_date, period, completed_steps, notes, completed):
    log = db.scalar(
        select(RoutineLog).where(
            RoutineLog.user_id == user_id,
            RoutineLog.log_date == log_date,
            RoutineLog.period == period,
        )
    )
    if log is None:
        log = RoutineLog(user_id=user_id, log_date=log_date, period=period)
        db.add(log)
    log.completed_steps = list(dict.fromkeys(completed_steps))
    log.notes = notes
    log.completed = completed
    db.flush()
    return log


def get_day(db, user_id, on_date):
    logs = db.scalars(
        select(RoutineLog).where(RoutineLog.user_id == user_id, RoutineLog.log_date == on_date)
    ).all()
    periods = {log.period: log for log in logs}
    return periods.get("AM"), periods.get("PM")


def streak_days(db, user_id, on_date):
    # A day counts when at least one entire period was completed.
    dates = set(
        db.scalars(
            select(RoutineLog.log_date).where(
                RoutineLog.user_id == user_id,
                RoutineLog.completed.is_(True),
                RoutineLog.log_date <= on_date,
            )
        ).all()
    )
    cursor = on_date if on_date in dates else on_date - timedelta(days=1)
    count = 0
    while cursor in dates:
        count += 1
        cursor -= timedelta(days=1)
    return count
