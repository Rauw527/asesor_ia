"""User aggregate root."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.types import UTCDateTime, new_id, utcnow

# Importación en tiempo de ejecución (no solo TYPE_CHECKING) para que
# SQLAlchemy pueda resolver las clases relacionadas en las relaciones.
from app.models.consent import Consent  # noqa: F401
from app.models.photo import Photo  # noqa: F401
from app.models.questionnaire import Questionnaire  # noqa: F401
from app.models.skin_analysis import SkinAnalysis  # noqa: F401
from app.models.skin_assessment import SkinAssessment  # noqa: F401
from app.models.routine import Routine  # noqa: F401

if TYPE_CHECKING:
    from app.models.catalog_product import CatalogProduct
    from app.models.product import Product
    from app.models.routine_log import RoutineLog
    from app.models.skin_evolution_log import SkinEvolutionLog
    from app.models.skin_profile import SkinProfile


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=new_id)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(120), default="")
    password_hash: Mapped[str | None] = mapped_column(String(255), default=None)
    onboarding_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utcnow, onupdate=utcnow)

    skin_profile: Mapped[SkinProfile | None] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    products: Mapped[list[Product]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    routine_logs: Mapped[list[RoutineLog]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    evolution_logs: Mapped[list[SkinEvolutionLog]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    consents: Mapped[list[Consent]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    photos: Mapped[list[Photo]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    questionnaires: Mapped[list[Questionnaire]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    skin_analyses: Mapped[list[SkinAnalysis]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    skin_assessments: Mapped[list[SkinAssessment]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    routines: Mapped[list[Routine]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"<User {self.email}>"
