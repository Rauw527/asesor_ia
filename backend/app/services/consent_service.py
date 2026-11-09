"""Consent business logic (A: service, B: training)."""

from __future__ import annotations

from fastapi import HTTPException, status

from app.repositories import consent_repository
from app.schemas.consent import ConsentCreate, ConsentOut


def save_consent(db, user_id: str, payload: ConsentCreate) -> ConsentOut:
    consent = consent_repository.grant_consent(
        db,
        user_id=user_id,
        consent_type=payload.consent_type,
        granted=payload.granted,
        version=payload.version,
        purpose=payload.purpose,
    )
    db.commit()
    return ConsentOut.model_validate(consent)


def list_user_consents(db, user_id: str) -> list[ConsentOut]:
    consents = consent_repository.list_consents(db, user_id)
    return [ConsentOut.model_validate(c) for c in consents]


def is_training_consent_granted(db, user_id: str) -> bool:
    c = consent_repository.get_consent(db, user_id, "training")
    return bool(c and c.granted)
