"""Skin analysis business logic."""

from __future__ import annotations

from app.repositories import skin_analysis_repository
from app.services.ai.engine import SkinAnalysisEngine

engine = SkinAnalysisEngine()


async def run_analysis(db, user_id: str, photo_ids: list[str], photo_paths: list[str]):
    """Run analysis and persist the result."""
    result = await engine.analyze(photo_paths)
    analysis = skin_analysis_repository.save_analysis(
        db,
        user_id=user_id,
        photo_ids=photo_ids,
        analysis_status=result.analysis_status,
        model_version=result.model_version,
        observations=result.observations,
        confidence=result.confidence,
        limitations=result.limitations,
    )
    db.commit()
    return analysis


def list_user_analyses(db, user_id: str):
    return skin_analysis_repository.list_analyses(db, user_id)


def get_analysis(db, analysis_id: str, user_id: str):
    return skin_analysis_repository.get_analysis(db, analysis_id, user_id)
