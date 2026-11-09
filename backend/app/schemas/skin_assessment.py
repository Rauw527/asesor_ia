"""Skin assessment contracts."""

from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, ConfigDict


class SkinAssessmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    perceived_skin_type: str | None
    sensitivity: str | None
    main_concerns: list[str]
    questionnaire_completed: bool
    visual_analysis_status: str
    data_source: str
    created_at: datetime
    updated_at: datetime
