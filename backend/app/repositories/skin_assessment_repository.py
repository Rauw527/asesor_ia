"""Skin assessment persistence helpers."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.skin_assessment import SkinAssessment


def save_assessment(
    db: Session,
    user_id: str,
    perceived_skin_type: str | None,
    sensitivity: str | None,
    main_concerns: list[str],
    questionnaire_completed: bool,
    visual_analysis_status: str,
    data_source: str,
) -> SkinAssessment:
    existing = db.execute(
        select(SkinAssessment).where(SkinAssessment.user_id == user_id)
    ).scalar_one_or_none()

    if existing:
        existing.perceived_skin_type = perceived_skin_type
        existing.sensitivity = sensitivity
        existing.main_concerns = main_concerns
        existing.questionnaire_completed = questionnaire_completed
        existing.visual_analysis_status = visual_analysis_status
        existing.data_source = data_source
        db.add(existing)
        db.flush()
        return existing

    assessment = SkinAssessment(
        user_id=user_id,
        perceived_skin_type=perceived_skin_type,
        sensitivity=sensitivity,
        main_concerns=main_concerns,
        questionnaire_completed=questionnaire_completed,
        visual_analysis_status=visual_analysis_status,
        data_source=data_source,
    )
    db.add(assessment)
    db.flush()
    return assessment


def get_assessment(db: Session, user_id: str) -> SkinAssessment | None:
    return db.execute(
        select(SkinAssessment).where(SkinAssessment.user_id == user_id)
    ).scalar_one_or_none()
