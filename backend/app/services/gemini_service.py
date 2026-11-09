"""Gemini vision adapter.

All model calls live here so the rest of the application depends on plain
Pydantic objects instead of SDK types. Structured output is enforced with
``response_mime_type="application/json"`` plus a ``response_schema``, which is
the only reliable way to keep a vision model inside a contract.
"""

from __future__ import annotations

import json
import logging
import time
from typing import Any, TypeVar

from google import genai
from google.genai import types
from pydantic import BaseModel, ValidationError

from app.core.config import Settings
from app.schemas.llm import (
    LLMInciScan,
    LLMSafeAlternative,
    LLMSkinAnalysis,
    LLMSkinProgress,
)
from app.services.image_service import PreparedImage

logger = logging.getLogger(__name__)

SchemaT = TypeVar("SchemaT", bound=BaseModel)

COSMETIC_DISCLAIMER = (
    "Este análisis es estrictamente cosmético y estimativo; no sustituye el "
    "diagnóstico ni el tratamiento de un dermatólogo."
)

SKIN_ANALYSIS_PROMPT = f"""
Actúa como asesor de imagen y cuidado facial con formación en cosmética.
Analiza la selfie adjunta y devuelve un diagnóstico COSMÉTICO en español.

Reglas obligatorias:
1. Evalúa únicamente rasgos visibles: brillo, textura, poros, rojeces, manchas,
   deshidratación aparente y subtono de piel.
2. No menciones ni diagnostiques enfermedades, infecciones, acné quístico,
   rosácea, dermatitis ni ninguna condición médica.
3. Si la imagen no muestra un rostro humano claro, está muy oscura, borrosa o
   tapada, pon is_valid_face=false y explica el motivo en invalid_reason.
4. hydration_level es una estimación conservadora de 0 a 100 basada en brillo,
   líneas finas y opacidad; nunca lo infles.
5. detected_issues: máximo 5 hallazgos, redactados como observaciones
   ("Zona T oleosa", "Manchas leves en mejillas"), nunca como diagnósticos.
6. recommendations: máximo 5 acciones concretas de rutina (paso, frecuencia,
   momento del día).
7. product_suggestions: entre 1 y 5 productos comerciales reales y vigentes.
   Devuelve solo name, brand y reason. NUNCA inventes enlaces.
8. disclaimer debe ser exactamente este texto:
   "{COSMETIC_DISCLAIMER}"
""".strip()

SKIN_PROGRESS_PROMPT = """
Actúa como asesor cosmético comparando la evolución de una piel.
Recibes dos fotos de la MISMA persona: la primera es la línea base (semana 1) y
la segunda es el chequeo actual (semana 4). Devuelve la comparación en español.

Reglas obligatorias:
1. Compara solo lo visible: rojeces, manchas, textura, brillo y luminosidad.
2. progress_percentage es una estimación conservadora de mejora global (0-100).
   Si las fotos tienen iluminación muy distinta, dilo en summary_notes y baja la
   confianza del porcentaje.
3. hydration_change y texture_improvement deben describir el cambio observado
   con dirección ("+15% mayor hidratación", "Reducción visible de rojeces en
   zona T").
4. recommended_routine_adjustments: entre 1 y 4 ajustes concretos y accionables.
5. No emitas diagnósticos médicos ni prometas resultados clínicos.
""".strip()

INCI_SCAN_PROMPT = """
Actúa como experto en formulación cosmética leyendo el reverso de un producto.
La imagen contiene una etiqueta con la lista INCI (INCI list / ingredients).

Reglas obligatorias:
1. Si no hay una lista de ingredientes legible, pon is_readable_label=false y
   deja key_ingredients vacío.
2. product_name: el nombre comercial visible en el envase; si no es legible usa
   "Producto sin identificar".
3. key_ingredients: hasta 20 ingredientes relevantes, escritos como aparecen en
   la etiqueta (sin traducir), priorizando activos, exfoliantes, retinoides,
   fragancias, alcohol y filtros solares.
4. has_conflict y conflict_reason: evalúa SOLO incompatibilidades cosméticas
   conocidas entre los ingredientes del producto y los de la rutina activa que
   se te indica. No inventes conflictos ni recomiendes suspender tratamientos
   médicos.
5. Responde en español para conflict_reason.
""".strip()

SAFE_ALTERNATIVE_PROMPT = """
Actúa como asesor cosmético proponiendo UNA alternativa segura.
Recibes un conflicto de ingredientes detectado y el perfil de piel del usuario.
Devuelve un producto comercial real (name con marca incluida) que evite ambos
ingredientes y un reason breve en español. No inventes enlaces ni precios.
""".strip()

_TRANSIENT_CODES = {429, 500, 502, 503, 504}


class GeminiError(RuntimeError):
    """Base error surfaced to the API layer as JSON."""

    status_code = 502

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class GeminiNotConfigured(GeminiError):
    status_code = 503


class GeminiCallFailed(GeminiError):
    status_code = 502


class GeminiInvalidResponse(GeminiError):
    status_code = 502


class UnusableImage(GeminiError):
    """The model could not use the image (no face / unreadable label)."""

    status_code = 422


class GeminiService:
    def __init__(self, config: Settings) -> None:
        self._config = config
        self._client: genai.Client | None = None

    # ------------------------------------------------------------------ setup
    def _get_client(self) -> genai.Client:
        if not self._config.gemini_enabled:
            raise GeminiNotConfigured(
                "GEMINI_API_KEY no está configurada. Añádela al archivo .env del "
                "backend para habilitar los análisis con IA."
            )
        if self._client is None:
            self._client = genai.Client(
                api_key=self._config.gemini_api_key,
                http_options=types.HttpOptions(timeout=self._config.gemini_timeout_seconds * 1000),
            )
        return self._client

    # --------------------------------------------------------------- public API
    def analyze_skin(self, image: PreparedImage) -> LLMSkinAnalysis:
        result = self._generate(
            prompt=SKIN_ANALYSIS_PROMPT,
            images=[image],
            schema=LLMSkinAnalysis,
            temperature=0.2,
        )
        if not result.is_valid_face:
            raise UnusableImage(
                result.invalid_reason
                or "No se detectó un rostro claro en la foto. Repite la captura "
                "con luz frontal y el óvalo de encuadre completo."
            )
        return result

    def compare_progress(
        self,
        baseline: PreparedImage,
        current: PreparedImage,
        baseline_context: str,
        days_elapsed: int | None = None,
    ) -> LLMSkinProgress:
        context_lines = [SKIN_PROGRESS_PROMPT, "", "Contexto de la línea base:"]
        context_lines.append(baseline_context or "Sin diagnóstico previo registrado.")
        if days_elapsed:
            context_lines.append(f"Días transcurridos entre ambas fotos: {days_elapsed}.")
        context_lines.append(
            "La primera imagen es Día 1 / Semana 1. La segunda es el chequeo actual."
        )
        return self._generate(
            prompt="\n".join(context_lines),
            images=[baseline, current],
            schema=LLMSkinProgress,
            temperature=0.2,
        )

    def read_inci_label(self, image: PreparedImage) -> LLMInciScan:
        result = self._generate(
            prompt=INCI_SCAN_PROMPT,
            images=[image],
            schema=LLMInciScan,
            temperature=0.1,
        )
        if not result.is_readable_label or not result.key_ingredients:
            raise UnusableImage(
                "No se pudo leer la lista INCI. Acerca la cámara a la etiqueta, "
                "evita reflejos y asegúrate de que el texto esté enfocado."
            )
        return result

    def suggest_safe_alternative(
        self, conflict_description: str, skin_type: str | None
    ) -> LLMSafeAlternative:
        prompt = (
            f"{SAFE_ALTERNATIVE_PROMPT}\n\n"
            f"Conflicto detectado: {conflict_description}\n"
            f"Tipo de piel del usuario: {skin_type or 'sin dato'}"
        )
        return self._generate(
            prompt=prompt,
            images=[],
            schema=LLMSafeAlternative,
            temperature=0.4,
        )

    # ------------------------------------------------------------------ internals
    def _generate(
        self,
        *,
        prompt: str,
        images: list[PreparedImage],
        schema: type[SchemaT],
        temperature: float,
    ) -> SchemaT:
        client = self._get_client()
        contents: list[Any] = [
            types.Part.from_bytes(data=image.data, mime_type=image.mime_type) for image in images
        ]
        contents.append(prompt)

        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=schema,
            temperature=temperature,
            max_output_tokens=self._config.gemini_max_output_tokens,
        )

        last_error: Exception | None = None
        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model=self._config.gemini_model,
                    contents=contents,
                    config=config,
                )
            except Exception as exc:  # noqa: BLE001 - SDK raises many types
                last_error = exc
                if attempt == 0 and _is_transient(exc):
                    logger.warning("Transient Gemini error, retrying: %s", exc)
                    time.sleep(1.5)
                    continue
                raise GeminiCallFailed(f"El servicio de IA falló: {_describe_error(exc)}") from exc

            parsed = _parse_structured(response, schema)
            if parsed is not None:
                return parsed

            # A safety block or a truncated response is not retryable.
            raise GeminiInvalidResponse(
                "La IA no devolvió un JSON válido para el esquema solicitado "
                f"(modelo {self._config.gemini_model}). Revisa la imagen e "
                "inténtalo de nuevo."
            )

        raise GeminiCallFailed(f"El servicio de IA falló: {last_error}")


def _is_transient(exc: Exception) -> bool:
    code = getattr(exc, "code", None) or getattr(exc, "status_code", None)
    return code in _TRANSIENT_CODES


def _describe_error(exc: Exception) -> str:
    message = str(exc).strip() or exc.__class__.__name__
    return message if len(message) <= 300 else message[:300] + "…"


def _parse_structured(response: Any, schema: type[SchemaT]) -> SchemaT | None:
    parsed = getattr(response, "parsed", None)
    if isinstance(parsed, schema):
        return parsed
    if isinstance(parsed, dict):
        try:
            return schema.model_validate(parsed)
        except ValidationError:
            pass

    text = getattr(response, "text", None)
    if text:
        try:
            return schema.model_validate(json.loads(text))
        except (json.JSONDecodeError, ValidationError) as exc:
            logger.warning("Unparseable Gemini payload: %s", exc)
    return None


def build_gemini_service(config: Settings) -> GeminiService:
    return GeminiService(config)
