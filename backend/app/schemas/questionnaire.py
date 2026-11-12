"""Questionnaire request/response contracts."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AnswerIn(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    question_key: str = Field(min_length=1, max_length=100)
    answer_value: str
    answer_type: str = Field(default="single", max_length=30)


class QuestionnaireCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    answers: list[AnswerIn] = Field(default_factory=list)


class AnswerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    question_key: str
    answer_value: str
    answer_type: str


class QuestionnaireOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    completed: bool
    created_at: datetime
    answers: list[AnswerOut] = []
