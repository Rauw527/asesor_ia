"""SkinProfile and SkinEvolutionLog persistence."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import SkinEvolutionLog, SkinProfile, User
from app.models.types import utcnow


def upsert_profile(db: Session, user: User, analysis) -> SkinProfile:  # noqa: ANN001
    profile = user.skin_profile
    if profile is None:
        profile = SkinProfile(user_id=user.id)
        db.add(profile)
        user.skin_profile = profile

    profile.skin_type = analysis.skin_type
    profile.hydration_level = analysis.hydration_level
    profile.undertone = analysis.undertone
    profile.detected_issues = list(analysis.detected_issues)
    profile.recommendations = list(analysis.recommendations)
    profile.last_analyzed_at = utcnow()
    user.onboarding_completed = True
    db.flush()
    return profile


def add_evolution_log(
    db: Session,
    *,
    user_id: str,
    image_path: str,
    week_number: int,
    is_baseline: bool,
    skin_type: str | None = None,
    hydration_level: int | None = None,
    undertone: str | None = None,
    detected_issues: list[str] | None = None,
    progress_percentage: int | None = None,
    summary_notes: str = "",
    captured_at: datetime | None = None,
) -> SkinEvolutionLog:
    log = SkinEvolutionLog(
        user_id=user_id,
        image_path=image_path,
        week_number=week_number,
        is_baseline=is_baseline,
        skin_type=skin_type,
        hydration_level=hydration_level,
        undertone=undertone,
        detected_issues=list(detected_issues or []),
        progress_percentage=progress_percentage,
        summary_notes=summary_notes,
        captured_at=captured_at or utcnow(),
    )
    db.add(log)
    db.flush()
    return log


def list_logs(db: Session, user_id: str) -> list[SkinEvolutionLog]:
    return list(
        db.scalars(
            select(SkinEvolutionLog)
            .where(SkinEvolutionLog.user_id == user_id)
            .order_by(SkinEvolutionLog.captured_at.desc())
        )
    )


def get_baseline(db: Session, user_id: str) -> SkinEvolutionLog | None:
    return db.scalar(
        select(SkinEvolutionLog)
        .where(
            SkinEvolutionLog.user_id == user_id,
            SkinEvolutionLog.is_baseline.is_(True),
        )
        .order_by(SkinEvolutionLog.captured_at.asc())
        .limit(1)
    )


def count_logs(db: Session, user_id: str) -> int:
    return int(
        db.scalar(
            select(func.count())
            .select_from(SkinEvolutionLog)
            .where(SkinEvolutionLog.user_id == user_id)
        )
        or 0
    )
