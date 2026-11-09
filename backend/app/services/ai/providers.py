"""Pluggable skin analysis providers.

The default provider is a clearly identified demo implementation. It does not
invent predictions; all observations are null and the status is "demo".
Replace this provider with PyTorch/OpenCV or a multimodal API later without
changing the contract.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AnalysisResult:
    analysis_status: str
    model_version: str | None
    observations: dict
    confidence: float | None
    limitations: list[str]


class SkinAnalysisProvider:
    """Interface for skin visual analysis."""

    async def analyze(self, photo_paths: list[str]) -> AnalysisResult:  # noqa: ARG002
        raise NotImplementedError


class DemoAnalysisProvider(SkinAnalysisProvider):
    """Demo provider: clearly identified, no real predictions."""

    def __init__(self) -> None:
        self.model_version = None

    async def analyze(self, photo_paths: list[str]) -> AnalysisResult:
        return AnalysisResult(
            analysis_status="demo",
            model_version=None,
            observations={
                "visibleAcne": None,
                "visibleSpots": None,
                "redness": None,
                "shine": None,
                "texture": None,
            },
            confidence=None,
            limitations=[
                "Análisis visual de demostración: resultados orientativos, todavía no generados por un modelo de IA validado.",
                "No se han entrenado modelos propios; las observaciones son nulas por diseño.",
            ],
        )
