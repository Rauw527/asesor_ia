"""Photo request/response contracts."""

from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class PhotoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    photo_type: str
    storage_path: str
    original_filename: str | None
    content_type: str
    size_bytes: int
    consent_version: str | None
    uploaded_at: datetime


class PhotoUploadResponse(BaseModel):
    photo_id: str
    photo_type: str
    message: str
