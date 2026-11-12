"""Skin analysis persistence helpers."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.skin_analysis import SkinAnalysis


def save_analysis(
    db: Session,
    user_id: str,
    photo_ids: list[str],
    analysis_status: str,
    model_version: str | None,
    observations: dict,
    confidence: float | None,
    limitations: list[str],
) -> SkinAnalysis:
    analysis = SkinAnalysis(
        user_id=user_id,
        photo_ids=photo_ids,
        analysis_status=analysis_status,
        model_version=model_version,
        observations=observations,
        confidence=confidence,
        limitations=limitations,
    )
    db.add(analysis)
    db.flush()
    return analysis


def list_analyses(db: Session, user_id: str) -> list[SkinAnalysis]:
    return list(
        db.execute(
            select(SkinAnalysis)
            .where(SkinAnalysis.user_id == user_id)
            .order_by(SkinAnalysis.created_at.desc())
        ).scalars()
    )


def get_analysis(db: Session, analysis_id: str, user_id: str) -> SkinAnalysis | None:
    return db.execute(
        select(SkinAnalysis).where(SkinAnalysis.id == analysis_id, SkinAnalysis.user_id == user_id)
    ).scalar_one_or_none()
