"""Skincare use cases: diagnosis, monthly comparison and history."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from app.core.config import Settings
from app.models import SkinEvolutionLog, User
from app.models.types import utcnow
from app.repositories import skin_repository
from app.schemas.llm import LLMSkinAnalysis
from app.schemas.skin import ProductSuggestion, SkinAnalysisResponse, SkinProgressResponse
from app.schemas.user import EvolutionHistoryResponse, EvolutionLogOut
from app.services.affiliate import build_affiliate_link
from app.services.gemini_service import COSMETIC_DISCLAIMER, GeminiService
from app.services.image_service import PreparedImage
from app.services.storage import StorageBackend

_MAX_PRODUCTS = 5
_MAX_ISSUES = 5
_MAX_RECOMMENDATIONS = 5


def _aware(value: datetime) -> datetime:
    return value if value.tzinfo else value.replace(tzinfo=utcnow().tzinfo)


def week_number_for(baseline: SkinEvolutionLog | None, reference: datetime) -> int:
    if baseline is None:
        return 1
    elapsed_days = max(0, (reference - _aware(baseline.captured_at)).days)
    return max(1, elapsed_days // 7 + 1)


def _baseline_context(profile, baseline: SkinEvolutionLog | None) -> str:
    parts: list[str] = []
    if profile and profile.skin_type:
        parts.append(f"Tipo de piel: {profile.skin_type}.")
    if profile and profile.undertone:
        parts.append(f"Subtono: {profile.undertone}.")
    issues = (profile.detected_issues if profile else None) or (
        baseline.detected_issues if baseline else None
    )
    if issues:
        parts.append("Hallazgos iniciales: " + ", ".join(issues) + ".")
    if profile and profile.hydration_level is not None:
        parts.append(f"Hidratación inicial estimada: {profile.hydration_level}%.")
    return " ".join(parts)


def to_public_analysis(analysis: LLMSkinAnalysis, config: Settings) -> SkinAnalysisResponse:
    suggestions = [
        ProductSuggestion(
            name=product.name,
            brand=product.brand,
            reason=product.reason,
            # Links are generated here, never by the model.
            affiliate_link=build_affiliate_link(config, product.brand, product.name),
        )
        for product in analysis.product_suggestions[:_MAX_PRODUCTS]
    ]
    return SkinAnalysisResponse(
        skin_type=analysis.skin_type,
        hydration_level=max(0, min(100, analysis.hydration_level)),
        undertone=analysis.undertone,
        detected_issues=analysis.detected_issues[:_MAX_ISSUES],
        recommendations=analysis.recommendations[:_MAX_RECOMMENDATIONS],
        product_suggestions=suggestions,
        disclaimer=COSMETIC_DISCLAIMER,
    )


def analyze(
    db: Session,
    *,
    user: User,
    image: PreparedImage,
    gemini: GeminiService,
    storage: StorageBackend,
    config: Settings,
) -> SkinAnalysisResponse:
    result = gemini.analyze_skin(image)
    image_path = storage.save(image.data, "skin")

    baseline = skin_repository.get_baseline(db, user.id)
    is_baseline = baseline is None
    captured_at = utcnow()
    week = 1 if is_baseline else week_number_for(baseline, captured_at)

    skin_repository.upsert_profile(db, user, result)
    skin_repository.add_evolution_log(
        db,
        user_id=user.id,
        image_path=image_path,
        week_number=week,
        is_baseline=is_baseline,
        skin_type=result.skin_type,
        hydration_level=result.hydration_level,
        undertone=result.undertone,
        detected_issues=result.detected_issues,
        summary_notes=f"Diagnóstico inicial (semana {week}).",
        captured_at=captured_at,
    )
    db.commit()
    return to_public_analysis(result, config)


def compare_progress(
    db: Session,
    *,
    user: User,
    baseline_image: PreparedImage,
    current_image: PreparedImage,
    days_elapsed: int | None,
    gemini: GeminiService,
    storage: StorageBackend,
    config: Settings,
) -> SkinProgressResponse:
    baseline_log = skin_repository.get_baseline(db, user.id)
    profile = user.skin_profile
    context = _baseline_context(profile, baseline_log)

    if days_elapsed is None and baseline_log is not None:
        days_elapsed = max(0, (utcnow() - _aware(baseline_log.captured_at)).days)

    result = gemini.compare_progress(
        baseline_image, current_image, context, days_elapsed=days_elapsed
    )

    current_path = storage.save(current_image.data, "skin")
    # Keep the baseline photo the user uploaded when no baseline row exists yet
    # (e.g. the user skipped onboarding on this device).
    if baseline_log is None:
        storage.save(baseline_image.data, "skin")

    skin_repository.add_evolution_log(
        db,
        user_id=user.id,
        image_path=current_path,
        week_number=week_number_for(baseline_log, utcnow()),
        is_baseline=False,
        skin_type=profile.skin_type if profile else None,
        hydration_level=profile.hydration_level if profile else None,
        undertone=profile.undertone if profile else None,
        detected_issues=profile.detected_issues if profile else [],
        progress_percentage=result.progress_percentage,
        summary_notes=result.summary_notes,
    )
    db.commit()

    return SkinProgressResponse(
        progress_percentage=max(0, min(100, result.progress_percentage)),
        hydration_change=result.hydration_change,
        texture_improvement=result.texture_improvement,
        summary_notes=result.summary_notes,
        recommended_routine_adjustments=result.recommended_routine_adjustments,
    )


def history(db: Session, *, user: User, storage: StorageBackend) -> EvolutionHistoryResponse:
    logs = skin_repository.list_logs(db, user.id)
    items: list[EvolutionLogOut] = []
    for log in logs:
        payload = EvolutionLogOut.model_validate(log)
        payload.image_url = storage.url_for(log.image_path)
        items.append(payload)
    return EvolutionHistoryResponse(items=items)


__all__ = [
    "analyze",
    "compare_progress",
    "history",
    "to_public_analysis",
    "week_number_for",
]
