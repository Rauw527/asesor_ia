"""Questionnaire business logic."""

from __future__ import annotations

from app.repositories import questionnaire_repository
from app.schemas.questionnaire import QuestionnaireCreate, QuestionnaireOut


def save_questionnaire(db, user_id: str, payload: QuestionnaireCreate) -> QuestionnaireOut:
    answers = [
        {
            "question_key": a.question_key,
            "answer_value": a.answer_value,
            "answer_type": a.answer_type,
        }
        for a in payload.answers
    ]
    questionnaire = questionnaire_repository.save_questionnaire(db, user_id, answers)
    db.commit()
    return QuestionnaireOut.model_validate(questionnaire)


def get_latest_questionnaire(db, user_id: str) -> QuestionnaireOut | None:
    q = questionnaire_repository.get_latest_questionnaire(db, user_id)
    if not q:
        return None
    return QuestionnaireOut.model_validate(q)
