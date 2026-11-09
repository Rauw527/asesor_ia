"""Consent persistence helpers."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.consent import Consent
from app.models.types import utcnow


def grant_consent(
    db: Session,
    user_id: str,
    consent_type: str,
    granted: bool,
    version: str = "1.0",
    purpose: str | None = None,
) -> Consent:
    existing = db.execute(
        select(Consent).where(
            Consent.user_id == user_id, Consent.consent_type == consent_type
        )
    ).scalar_one_or_none()

    now = utcnow()
    if existing:
        existing.granted = granted
        existing.version = version
        existing.purpose = purpose
        if granted and not existing.granted:
            existing.granted_at = now
        if not granted:
            existing.withdrawn_at = now
        db.add(existing)
        db.flush()
        return existing

    consent = Consent(
        user_id=user_id,
        consent_type=consent_type,
        granted=granted,
        version=version,
        purpose=purpose,
        granted_at=now if granted else None,
    )
    db.add(consent)
    db.flush()
    return consent


def list_consents(db: Session, user_id: str) -> list[Consent]:
    return list(
        db.execute(select(Consent).where(Consent.user_id == user_id)).scalars()
    )


def get_consent(db: Session, user_id: str, consent_type: str) -> Consent | None:
    return db.execute(
        select(Consent).where(
            Consent.user_id == user_id, Consent.consent_type == consent_type
        )
    ).scalar_one_or_none()
