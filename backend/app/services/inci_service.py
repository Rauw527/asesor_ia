"""INCI scanner use case (OCR via Gemini + deterministic rule engine)."""

from __future__ import annotations

import hashlib
import logging

from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.models import User
from app.repositories import product_repository
from app.schemas.inci import INCIScanResponse, SafeAlternative
from app.schemas.llm import LLMInciScan
from app.services import inci_rules
from app.services.affiliate import build_affiliate_link
from app.services.cache import CacheBackend
from app.services.gemini_service import GeminiError, GeminiService
from app.services.image_service import PreparedImage
from app.services.storage import StorageBackend

logger = logging.getLogger(__name__)


def _ocr_cache_key(image: PreparedImage) -> str:
    return f"inci:ocr:{image.sha256}"


def _alternative_cache_key(warning: str, skin_type: str | None) -> str:
    digest = hashlib.sha256(f"{warning}|{skin_type or '-'}".encode()).hexdigest()
    return f"inci:alternative:{digest}"


def _read_label(
    image: PreparedImage, gemini: GeminiService, cache: CacheBackend, config: Settings
) -> tuple[LLMInciScan, bool]:
    key = _ocr_cache_key(image)
    cached = cache.get_json(key)
    if cached is not None:
        try:
            return LLMInciScan.model_validate(cached), True
        except ValidationError:
            logger.warning("Discarding incompatible cached INCI payload")

    result = gemini.read_inci_label(image)
    cache.set_json(key, result.model_dump(), config.inci_cache_ttl_seconds)
    return result, False


def _safe_alternative(
    *,
    warning: str,
    skin_type: str | None,
    gemini: GeminiService,
    cache: CacheBackend,
    config: Settings,
) -> SafeAlternative | None:
    key = _alternative_cache_key(warning, skin_type)
    cached = cache.get_json(key)
    if cached is not None:
        try:
            payload = SafeAlternative.model_validate(cached)
            payload.affiliate_link = build_affiliate_link(config, payload.name)
            return payload
        except ValidationError:
            logger.warning("Discarding incompatible cached alternative payload")

    try:
        suggestion = gemini.suggest_safe_alternative(warning, skin_type)
    except GeminiError as exc:
        # The conflict verdict is the valuable part; a missing alternative must
        # not turn a successful scan into a failed request.
        logger.warning("Safe alternative unavailable: %s", exc.message)
        return None

    alternative = SafeAlternative(
        name=suggestion.name,
        reason=suggestion.reason,
        affiliate_link=build_affiliate_link(config, suggestion.name),
    )
    cache.set_json(
        key,
        {
            "name": alternative.name,
            "reason": alternative.reason,
            "affiliate_link": alternative.affiliate_link,
        },
        config.inci_cache_ttl_seconds,
    )
    return alternative


def scan(
    db: Session,
    *,
    user: User,
    image: PreparedImage,
    gemini: GeminiService,
    cache: CacheBackend,
    storage: StorageBackend,
    config: Settings,
) -> INCIScanResponse:
    label, cache_hit = _read_label(image, gemini, cache, config)

    routine_ingredients = product_repository.active_ingredients(db, user.id)
    skin_type = user.skin_profile.skin_type if user.skin_profile else None
    verdict = inci_rules.evaluate(label.key_ingredients, routine_ingredients, skin_type)

    has_conflict = verdict.has_conflict or label.has_conflict
    warning_parts: list[str] = []
    if verdict.warning:
        warning_parts.append(verdict.warning)
    if label.has_conflict and label.conflict_reason:
        reason = label.conflict_reason.strip()
        if reason and reason not in warning_parts:
            warning_parts.append(reason)
    conflict_warning = " ".join(warning_parts) or None

    alternative = None
    if has_conflict and conflict_warning:
        alternative = _safe_alternative(
            warning=conflict_warning,
            skin_type=skin_type,
            gemini=gemini,
            cache=cache,
            config=config,
        )

    product_repository.upsert_product(
        db,
        user,
        name=label.product_name,
        key_ingredients=label.key_ingredients,
        is_active=False,
        source="inci_scan",
    )
    db.commit()

    logger.info(
        "INCI scan product=%s ingredients=%d conflict=%s cache_hit=%s",
        label.product_name,
        len(label.key_ingredients),
        has_conflict,
        cache_hit,
    )

    return INCIScanResponse(
        product_name=label.product_name,
        key_ingredients=label.key_ingredients,
        has_conflict=has_conflict,
        conflict_warning=conflict_warning,
        safe_alternative=alternative,
    )
