"""Questionnaire endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.questionnaire import (
    QuestionnaireCreate,
    QuestionnaireOut,
)
from app.services.questionnaire_service import (
    get_latest_questionnaire,
    save_questionnaire,
)

router = APIRouter(tags=["questionnaires"])


@router.post(
    "/questionnaires",
    response_model=QuestionnaireOut,
    status_code=201,
    summary="Guardar cuestionario de piel",
)
def save_questionnaire_endpoint(
    payload: QuestionnaireCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> QuestionnaireOut:
    return save_questionnaire(db, current_user.id, payload)


@router.get(
    "/questionnaires/latest",
    response_model=QuestionnaireOut | None,
    summary="Último cuestionario del usuario",
)
def get_latest_questionnaire_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> QuestionnaireOut | None:
    return get_latest_questionnaire(db, current_user.id)
