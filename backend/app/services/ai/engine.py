"""SkinAnalysisEngine: orchestrates the analysis provider."""

from __future__ import annotations

from app.services.ai.providers import AnalysisResult, DemoAnalysisProvider, SkinAnalysisProvider


class SkinAnalysisEngine:
    """Engine that delegates to a pluggable provider."""

    def __init__(self, provider: SkinAnalysisProvider | None = None) -> None:
        self.provider = provider or DemoAnalysisProvider()

    async def analyze(self, photo_paths: list[str]) -> AnalysisResult:
        return await self.provider.analyze(photo_paths)
