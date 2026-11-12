"""Consent enforcement. Training permission is never required for the service."""

from fastapi import HTTPException

from app.repositories import consent_repository
from app.schemas.consent import ConsentCreate, ConsentOut


def require_service_consent(db, user_id):
    consent = consent_repository.get_consent(db, user_id, "service")
    if not consent or not consent.granted:
        raise HTTPException(
            403, "Acepta el uso de fotografías para el servicio antes de subirlas o analizarlas."
        )
    return consent


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
    return [ConsentOut.model_validate(c) for c in consent_repository.list_consents(db, user_id)]


def is_training_consent_granted(db, user_id: str) -> bool:
    c = consent_repository.get_consent(db, user_id, "training")
    return bool(c and c.granted)
