"""Internal Gemini response schemas (never exposed directly to clients).

They intentionally omit affiliate links: URLs are generated server-side from a
configured template so the model cannot hallucinate dead or malicious links.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.skin import SkinType, Undertone


class LLMProductSuggestion(BaseModel):
    name: str = Field(description="Nombre comercial específico del producto")
    brand: str = Field(description="Marca del producto")
    reason: str = Field(description="Por qué este producto encaja con el diagnóstico")


class LLMSkinAnalysis(BaseModel):
    is_valid_face: bool = Field(
        description="False si la imagen no muestra un rostro humano claro y bien encuadrado"
    )
    invalid_reason: str | None = Field(
        default=None,
        description="Motivo por el que la imagen no sirve, solo cuando is_valid_face es False",
    )
    skin_type: SkinType = Field(description="Tipo de piel observado en la selfie")
    hydration_level: int = Field(description="Nivel de hidratación estimado, 0-100")
    undertone: Undertone = Field(description="Subtono de la piel")
    detected_issues: list[str] = Field(description="Hallazgos cosméticos visibles")
    recommendations: list[str] = Field(description="Recomendaciones de rutina")
    product_suggestions: list[LLMProductSuggestion] = Field(
        description="De 1 a 5 productos sustitutos o complementarios"
    )
    disclaimer: str = Field(description="Aviso de que el análisis es cosmético y no médico")


class LLMSkinProgress(BaseModel):
    progress_percentage: int = Field(description="Mejora global estimada, 0-100")
    hydration_change: str = Field(description="Cambio de hidratación percibido")
    texture_improvement: str = Field(description="Cambio de textura y rojeces")
    summary_notes: str = Field(description="Resumen cualitativo del avance")
    recommended_routine_adjustments: list[str] = Field(
        description="Ajustes concretos para el siguiente ciclo"
    )


class LLMInciScan(BaseModel):
    is_readable_label: bool = Field(
        description="False si no se puede leer una lista INCI en la imagen"
    )
    product_name: str = Field(description="Nombre del producto leído en la etiqueta")
    key_ingredients: list[str] = Field(
        description="Ingredientes INCI relevantes, en el orden de la etiqueta"
    )
    has_conflict: bool = Field(
        description="True si detectas una incompatibilidad con la rutina activa"
    )
    conflict_reason: str | None = Field(
        default=None, description="Explicación breve del conflicto detectado"
    )


class LLMSafeAlternative(BaseModel):
    name: str = Field(description="Producto alternativo seguro, con marca")
    reason: str = Field(description="Por qué es una alternativa segura")
