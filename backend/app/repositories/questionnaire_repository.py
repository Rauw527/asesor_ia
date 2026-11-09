"""Questionnaire persistence helpers."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.questionnaire import Questionnaire, QuestionnaireAnswer


def save_questionnaire(
    db: Session, user_id: str, answers: list[dict]
) -> Questionnaire:
    questionnaire = Questionnaire(user_id=user_id, completed=True)
    db.add(questionnaire)
    db.flush()

    for answer in answers:
        db.add(
            QuestionnaireAnswer(
                questionnaire_id=questionnaire.id,
                question_key=answer["question_key"],
                answer_value=answer["answer_value"],
                answer_type=answer.get("answer_type", "single"),
            )
        )
    db.flush()
    return questionnaire


def get_latest_questionnaire(db: Session, user_id: str) -> Questionnaire | None:
    return db.execute(
        select(Questionnaire)
        .where(Questionnaire.user_id == user_id)
        .order_by(Questionnaire.created_at.desc())
    ).scalars().first()
