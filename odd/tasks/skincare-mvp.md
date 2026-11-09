# Skincare MVP — Asesor IA (Fase 1)

Objetivo: MVP 100% funcional de un copiloto de imagen personal (Fase 1: skincare)
con FastAPI + Gemini Vision real y una app Flutter que capture fotos reales, sin
datos simulados. Rama: `master` (sin commits todavía). Entrega: monorepo único.
Runners: backend `.venv\Scripts\python.exe -m pytest`; mobile `flutter test`.

## Specs

S1 — Monorepo en `C:\Users\Administrador\Documents\proyect\asesor_ia` con
`backend/` y `mobile/`, más `docker-compose.yml` y `.gitignore` en la raíz.

S2 — Backend en FastAPI (Python 3.11+) con arquitectura por capas
(`api/`, `services/`, `repositories/`, `models/`, `schemas/`, `core/`).
`requirements.txt` debe incluir `fastapi`, `uvicorn`, `google-genai`,
`pydantic`, `sqlalchemy`, `python-multipart`.

S3 — Modelos SQLAlchemy: `User`, `SkinProfile`, `Product`, `INCI_Ingredient`,
`RoutineLog`, `SkinEvolutionLog`. `SkinProfile` incluye además
`colorimetry_season`, `body_shape`, `style_preference` para la Fase 2.

S4 — `app/services/gemini_service.py` usa `GEMINI_API_KEY` y fuerza JSON con
`response_mime_type="application/json"`. El modelo por defecto es
`gemini-flash-latest`, configurable con `GEMINI_MODEL`
(corrección: `gemini-1.5-flash` fue retirado por Google).

S5 — Endpoints requeridos, con prefijo `/api/v1`:
`POST /skin/analyze`, `POST /skin/compare-progress`, `POST /inci/scan`,
`POST /routine/checkin`.

S6 — CORS habilitado en `app/main.py` (origen `*` sin credenciales, configurable
por `CORS_ORIGINS`).

S7 — `SkinAnalysisResponse` expone exactamente: `skin_type`, `hydration_level`
(0–100), `undertone`, `detected_issues`, `recommendations`,
`product_suggestions`, `disclaimer`. `skin_type` ∈ {Mixta, Grasa, Seca,
Sensible, Normal}; `undertone` ∈ {Cálido, Frío, Neutro}.

S8 — Cada `product_suggestion` tiene `name`, `brand`, `reason`,
`affiliate_link`. El modelo nunca genera URLs: el backend compone el enlace con
`AFFILIATE_SEARCH_TEMPLATE` + `AFFILIATE_TAG`.

S9 — `SkinProgressResponse` expone exactamente: `progress_percentage`,
`hydration_change`, `texture_improvement`, `summary_notes`,
`recommended_routine_adjustments`.

S10 — `INCIScanResponse` expone exactamente: `product_name`, `key_ingredients`,
`has_conflict`, `conflict_warning`, `safe_alternative` (`name`, `reason`,
`affiliate_link`).

S11 — Persistencia PostgreSQL + pgvector con fallback SQLite por
`DATABASE_URL`; almacenamiento de imágenes en disco local servido en
`/api/v1/media` (interfaz preparada para S3/Firebase). La entrada de imagen es
`multipart/form-data`.

S12 — Flutter con dependencias `camera`, `http`, `image_picker`, `provider` y
carpetas `lib/views/`, `lib/controllers/`, `lib/models/`, `lib/services/`.

S13 — Pantallas: `main.dart`, `home_page.dart`, `face_scanner_page.dart`,
`skin_result_page.dart`, `skin_progress_page.dart`, `inci_scanner_page.dart`.

S14 — Captura real de cámara con `CameraController`; la galería es solo
fallback. Nada de imágenes mock en el flujo principal.

S15 — Calibrador de luz en cliente: luminancia media del preview
(`YUV420`/`BGRA`) con aviso de poca luz o luz excesiva antes de capturar.

S16 — Slider antes/después para la comparativa Día 1 vs. hoy.

S17 — Caché en memoria (TTL) para OCR INCI y alternativas; Redis opcional vía
`REDIS_URL`.

S18 — Slots de Fase 2 en base de datos y en el modelo Flutter
(`colorimetrySeason`, `bodyShape`, `stylePreference`).

S19 — `README.md` con comandos locales de `uvicorn` y `flutter run`.

S20 — Errores tipados: sin `GEMINI_API_KEY` → HTTP 503; imagen no usable
(rostro ausente o etiqueta ilegible) → HTTP 422.

S21 — Contratos de soporte necesarios para que el flujo sea real:
`GET /users/me`, `GET|POST /products`, `GET /routine/today`, `GET /skin/history`.

## Tasks

| ID | Specs | Ruta | Estado | Evidencia |
| --- | --- | --- | --- | --- |
| T1 | S1-S11, S20-S21 | inline | done | `backend/` completo; `pytest` 25 passed |
| T2 | S2, S4, S7-S11, S20 | inline | done | `tests/test_api.py` (15), `tests/test_inci_rules.py` (8) |
| T3 | S12, S18 | inline | done | modelos + `api_client` + `asesor_api` + `photo_store` |
| T4 | S13-S18 | inline | done | 5 controllers con `ChangeNotifier` |
| T5 | S14-S16 | inline | done | `camera_capture_view`, `before_after_slider`, `metric_card` |
| T6 | S13, S15-S16 | inline | done | `home`, `face_scanner`, `skin_result`, `skin_progress`, `inci_scanner`, `main.dart` |
| T7 | S14 | inline | done | `CAMERA` + cleartext + queries en AndroidManifest; claves de iOS |
| T8 | S12-S17 | inline | done | `flutter analyze` sin issues; `flutter test` 7 passed |
| T9 | S14 | inline | done | `flutter build apk --debug` → `app-debug.apk` |
| T10 | S19 | inline | done | `README.md` + este documento |

## Log

L1 — Requisitos originales (registrados en la sesión): MVP de "Asesor IA"
(copiloto de imagen y estilo, Fase 1 skincare) con backend FastAPI + Gemini
Vision, base de datos con pgvector/SQLite, app Flutter con cámara real,
diagnóstico facial, comparativa de progreso, auditoría INCI, tracker de rutina,
slider antes/después, calibrador de luz, caché INCI y slots de Fase 2.

L2 — Corrección de modelo: `gemini-1.5-flash` ya no existe en la API de Google
(verificado en `https://ai.google.dev/gemini-api/docs/models`). Se usa
`gemini-flash-latest` por defecto y `GEMINI_MODEL` permite fijar una versión.

L3 — Supuestos aceptados: se añadió `Normal` al enum de tipo de piel; se
añadieron endpoints de productos y de usuario demo para que la auditoría INCI
tenga una rutina real contra la cual comparar.

L4 — Auditoría INCI: OCR con Gemini (cacheado por SHA-256) → motor determinista
de 39 ingredientes y 13 reglas de conflicto → segunda llamada Gemini (cacheada)
solo si hace falta una alternativa segura.

L5 — Verificación: backend `25 passed`; `ruff check`/`ruff format` limpios;
`POST /skin/analyze` sin API key responde 503 `ai_unavailable`; Flutter
`analyze` limpio, `test` 7/7, APK debug compilado.

L6 — Limitación conocida: no hay `GEMINI_API_KEY` en este entorno, por lo que
las llamadas reales a Gemini no se pudieron ejecutar de extremo a extremo; sí
están cubiertas con dobles de prueba y la ruta de error 503.

L7 — Las licencias del Android SDK estaban pendientes; el primer
`flutter build apk` instaló `android-35` y compiló correctamente.

L8 — Endurecimiento: todos los controllers capturan también errores no
previstos (no solo `ApiException`) para que ninguna excepción asíncrona deje la
UI bloqueada; guardar la foto Día 1 devuelve un booleano y la UI muestra el
mensaje real. `flutter analyze` sigue limpio y `flutter test` 7/7.

L9 — El emulador `Medium_Phone_API_36.1` no arranca en este host (falla la
comprobación de hipervisor), así que no hubo verificación visual en runtime.
La evidencia de la app es: `flutter analyze` limpio, `flutter test` 7/7 y APK
debug compilado.

L10 — **Usuario (verbatim):** "estoy probando y me da error de conexion con el
Failed to load resource: net::ERR_CONNECTION_TIMED_OUT
10.0.2.2:8000/api/v1/routine/today?date=2026-11-04:1  Failed to load resource:
net::ERR_CONNECTION_TIMED_OUT".

Evidencia recogida: el backend responde `200` en `127.0.0.1:8000` desde Windows
(`/health` y `/api/v1/routine/today`), con `access-control-allow-origin: *`, y
escucha en `127.0.0.1:8000` (PID 17360, `uvicorn app.main:app --reload --port
8000`). `adb devices` no lista ningún dispositivo y no hay procesos
`qemu`/`emulator`. Los procesos `dart` muestran
`flutter_tools.snapshot run --dart-define=API_BASE_URL=http://10.0.2.2:8000`
compilando contra `flutter_web_sdk` (`dartdevc`), es decir: la app corre en
**Flutter web (Chrome)**, no en un emulador.

Causa raíz: `10.0.2.2` es el alias del host **solo dentro del emulador Android**.
En Chrome del propio PC esa IP no existe, así que el navegador agota el tiempo
(`ERR_CONNECTION_TIMED_OUT`) en lugar de recibir un `REFUSED`. El backend y CORS
estaban correctos; el fallo era la URL base.

Corrección: `AppConfig.apiBaseUrl` pasa de `const` a getter por plataforma —
`kIsWeb` → `http://localhost:8000`, Android → `http://10.0.2.2:8000`, resto →
`localhost`; `--dart-define=API_BASE_URL` sigue teniendo prioridad absoluta.
README actualizado (comandos por plataforma y dos filas de troubleshooting).
Verificación: `flutter analyze` sin issues, `flutter test` 7/7.
