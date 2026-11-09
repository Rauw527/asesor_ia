"""Consent endpoints (A: service, B: training)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.repositories import consent_repository
from app.schemas.consent import ConsentCreate, ConsentOut
from app.services.consent_service import (
    is_training_consent_granted,
    list_user_consents,
    save_consent,
)
from sqlalchemy.orm import Session

router = APIRouter(tags=["consents"])


@router.post(
    "/consents",
    response_model=ConsentOut,
    status_code=status.HTTP_201_CREATED,
    summary="Guardar o actualizar un consentimiento",
)
def save_consent_endpoint(
    payload: ConsentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ConsentOut:
    return save_consent(db, current_user.id, payload)


@router.get("/consents", response_model=list[ConsentOut], summary="Mis consentimientos")
def list_consents_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ConsentOut]:
    return list_user_consents(db, current_user.id)


@router.get(
    "/consents/training",
    summary="¿Está otorgado el consentimiento de entrenamiento (B)?",
)
def training_consent_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return {"granted": is_training_consent_granted(db, current_user.id)}
