"""Skin questionnaire and answers."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.types import UTCDateTime, new_id, utcnow

if TYPE_CHECKING:
    from app.models.user import User


class Questionnaire(Base):
    __tablename__ = "questionnaires"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=new_id)
    user_id: Mapped[str] = mapped_column(String(32), ForeignKey("users.id"), index=True)
    completed: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        UTCDateTime(), default=utcnow, onupdate=utcnow
    )

    user: Mapped["User"] = relationship(back_populates="questionnaires")
    answers: Mapped[list["QuestionnaireAnswer"]] = relationship(
        back_populates="questionnaire", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Questionnaire user={self.user_id} completed={self.completed}>"


class QuestionnaireAnswer(Base):
    __tablename__ = "questionnaire_answers"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=new_id)
    questionnaire_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("questionnaires.id"), index=True
    )
    question_key: Mapped[str] = mapped_column(String(100), index=True)
    answer_value: Mapped[str] = mapped_column(Text)
    answer_type: Mapped[str] = mapped_column(String(30), default="single")  # single, multi, text

    questionnaire: Mapped["Questionnaire"] = relationship(back_populates="answers")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Answer {self.question_key}={self.answer_value[:20]}>"
