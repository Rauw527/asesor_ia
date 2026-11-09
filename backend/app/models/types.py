"""Shared SQLAlchemy helpers and custom column types."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import JSON, DateTime, TypeDecorator
from sqlalchemy.types import TypeEngine

EMBEDDING_DIMENSIONS = 768


def new_id() -> str:
    return uuid.uuid4().hex


def utcnow() -> datetime:
    return datetime.now(UTC)


class UTCDateTime(DateTime):
    """Timezone-aware timestamp that stays consistent on SQLite."""

    def __init__(self) -> None:
        super().__init__(timezone=True)

    def process_bind_param(self, value, dialect):  # noqa: ANN001, ANN201
        if value is not None and value.tzinfo is None:
            value = value.replace(tzinfo=UTC)
        return value


class EmbeddingType(TypeDecorator[object]):
    """pgvector column on PostgreSQL, JSON list on SQLite.

    Phase 1 stores no embeddings; the column exists so Phase 2 can attach
    semantic ingredient matching without a migration of the reference table.
    """

    impl = JSON
    cache_ok = True

    def load_dialect_impl(self, dialect) -> TypeEngine:  # noqa: ANN001
        if dialect.name == "postgresql":
            from pgvector.sqlalchemy import Vector

            return dialect.type_descriptor(Vector(EMBEDDING_DIMENSIONS))
        return dialect.type_descriptor(JSON())
