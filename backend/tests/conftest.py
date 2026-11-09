"""Shared test fixtures.

The suite never touches the real Gemini API and never uses production data:
Gemini is replaced through FastAPI's dependency overrides and the database is a
throwaway SQLite file.
"""

from __future__ import annotations

import io
import os
import tempfile
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
_TEST_ROOT = Path(tempfile.mkdtemp(prefix="asesor_ia_tests_"))

os.environ["DATABASE_URL"] = f"sqlite:///{(_TEST_ROOT / 'test.db').as_posix()}"
os.environ["STORAGE_DIR"] = str(_TEST_ROOT / "storage")
os.environ["GEMINI_API_KEY"] = ""
os.environ["ENVIRONMENT"] = "test"
os.environ["LOG_LEVEL"] = "WARNING"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

from app.schemas.llm import (  # noqa: E402
    LLMInciScan,
    LLMProductSuggestion,
    LLMSafeAlternative,
    LLMSkinAnalysis,
    LLMSkinProgress,
)
from app.services.gemini_service import COSMETIC_DISCLAIMER, UnusableImage  # noqa: E402


def make_jpeg(color: tuple[int, int, int] = (196, 152, 128), size: int = 128) -> bytes:
    image = Image.new("RGB", (size, size), color)
    draw = ImageDraw.Draw(image)
    draw.ellipse((size * 0.2, size * 0.15, size * 0.8, size * 0.85), fill=(205, 165, 140))
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=90)
    return buffer.getvalue()


class FakeGemini:
    """Deterministic stand-in for ``GeminiService`` (no network, no key)."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []
        self.inci_analysis = LLMInciScan(
            is_readable_label=True,
            product_name="Serum Renovador Test",
            key_ingredients=["Aqua", "Retinol", "Glycolic Acid", "Niacinamide"],
            has_conflict=False,
            conflict_reason=None,
        )
        self.inci_error: Exception | None = None
        self.analyze_error: Exception | None = None

    # --- skincare
    def analyze_skin(self, image) -> LLMSkinAnalysis:  # noqa: ANN001
        self.calls.append(("analyze_skin", image.sha256))
        if self.analyze_error is not None:
            raise self.analyze_error
        return LLMSkinAnalysis(
            is_valid_face=True,
            invalid_reason=None,
            skin_type="Mixta",
            hydration_level=62,
            undertone="Cálido",
            detected_issues=["Zona T oleosa", "Manchas leves"],
            recommendations=["Limpiador suave AM/PM", "Protector solar SPF 50"],
            product_suggestions=[
                LLMProductSuggestion(
                    name="Gel Limpiador Suave",
                    brand="Marca Test",
                    reason="Respeta la barrera y controla el brillo de la zona T.",
                )
            ],
            disclaimer=COSMETIC_DISCLAIMER,
        )

    def compare_progress(self, baseline, current, baseline_context, days_elapsed=None):  # noqa: ANN001
        self.calls.append(("compare_progress", f"{baseline.sha256}:{current.sha256}"))
        return LLMSkinProgress(
            progress_percentage=28,
            hydration_change="+15% mayor hidratación",
            texture_improvement="Reducción visible de rojeces en zona T",
            summary_notes="Mejora moderada con iluminación comparable.",
            recommended_routine_adjustments=["Mantener niacinamida AM"],
        )

    # --- inci
    def read_inci_label(self, image) -> LLMInciScan:  # noqa: ANN001
        self.calls.append(("read_inci_label", image.sha256))
        if self.inci_error is not None:
            raise self.inci_error
        return self.inci_analysis

    def suggest_safe_alternative(self, conflict_description, skin_type):  # noqa: ANN001
        self.calls.append(("suggest_safe_alternative", conflict_description[:40]))
        return LLMSafeAlternative(
            name="Serum Alternativo Test",
            reason="Evita la combinación de retinol con AHA y mantiene la hidratación.",
        )

    def count(self, name: str) -> int:
        return sum(1 for call in self.calls if call[0] == name)


@pytest.fixture()
def fake_gemini() -> FakeGemini:
    return FakeGemini()


@pytest.fixture()
def client(fake_gemini: FakeGemini):
    from app.api.deps import get_gemini
    from app.core.database import get_engine, init_db
    from app.main import app
    from app.models import Base

    engine = get_engine()
    Base.metadata.drop_all(engine)
    init_db(engine)

    app.dependency_overrides[get_gemini] = lambda: fake_gemini
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def raw_client():
    """Client without the Gemini override (exercises the real adapter checks)."""
    from app.core.database import get_engine, init_db
    from app.main import app
    from app.models import Base

    engine = get_engine()
    Base.metadata.drop_all(engine)
    init_db(engine)

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def storage_dir() -> Path:
    return Path(os.environ["STORAGE_DIR"])


def upload(name: str, content: bytes, mime: str = "image/jpeg") -> dict:
    return {"file": (name, content, mime)}


__all__ = ["FakeGemini", "UnusableImage", "make_jpeg", "upload"]
