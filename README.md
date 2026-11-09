# Asesor IA — Personal Image & Style Co-Pilot

Phase 1 (Skincare) of a personal-image co-pilot: a **FastAPI** backend that
talks to **Gemini Vision** and a **Flutter** app that captures real photos,
audits cosmetic labels against a deterministic INCI rule engine, tracks the
daily routine and measures month-over-month skin progress.

No mocked analysis in the main flow: every diagnosis, comparison and label
reading goes through the live API. The only fakes live in the automated tests.

```
asesor_ia/
├── backend/                 FastAPI + SQLAlchemy + Gemini
│   ├── app/
│   │   ├── api/v1/routers/  skin, inci, routine, users (+ products)
│   │   ├── core/            settings, database, exceptions
│   │   ├── models/          User, SkinProfile, Product, INCI_Ingredient...
│   │   ├── repositories/    persistence helpers
│   │   ├── schemas/         public contracts + LLM DTOs
│   │   └── services/        gemini, skin, inci rules, storage, image
│   ├── tests/               25 backend tests
│   ├── Dockerfile
│   └── requirements.txt
├── mobile/                  Flutter app (Android first)
│   ├── lib/controllers/     5 ChangeNotifier controllers
│   ├── lib/models/          API models
│   ├── lib/services/        HTTP client, typed API facade, photo store
│   ├── lib/views/           home, scanner, result, progress, INCI
│   └── lib/widgets/         camera view, before/after slider, metric card
├── odd/tasks/skincare-mvp.md  Specs, tasks and verification log
├── docker-compose.yml       pgvector + redis + api
└── README.md
```

## Requirements

- Python 3.11+
- Flutter 3.41+ / Dart 3.11+
- A `GEMINI_API_KEY` from Google AI Studio (without it the API boots but every
  AI endpoint returns HTTP 503)
- Optional: Docker for PostgreSQL + pgvector + Redis

## Backend

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
Copy-Item .env.example .env      # then set GEMINI_API_KEY
uvicorn app.main:app --reload --port 8000
```

- Health: <http://localhost:8000/health>
- Swagger UI: <http://localhost:8000/docs>
- Default database: SQLite at `backend/data/asesor_ia.db` (zero setup)
- Demo user: created on first request (`demo@asesor.ia`)
- INCI seed: 39 ingredients and 13 conflict rules inserted on startup

### Docker (PostgreSQL + pgvector + Redis)

```powershell
Copy-Item backend/.env.example backend/.env   # set GEMINI_API_KEY
docker compose up --build
```

The compose file overrides `DATABASE_URL` and `REDIS_URL` to the containers.
Redis is optional: without it the INCI cache falls back to an in-process TTL
cache.

### Environment variables

| Variable | Default | Purpose |
| --- | --- | --- |
| `GEMINI_API_KEY` | — | Required for AI endpoints |
| `GEMINI_MODEL` | `gemini-flash-latest` | Override to pin an exact model |
| `GEMINI_TIMEOUT_SECONDS` | `60` | Per-request timeout |
| `DATABASE_URL` | SQLite file | `postgresql+psycopg://...` for pgvector |
| `REDIS_URL` | empty | Optional INCI cache |
| `AFFILIATE_SEARCH_TEMPLATE` | Amazon search | Affiliate URL template |
| `AFFILIATE_TAG` | empty | Tracking tag appended server-side |
| `MAX_UPLOAD_MB` | `8` | Upload limit |
| `IMAGE_MAX_SIDE` | `1024` | Server-side downscale before Gemini |
| `DEMO_USER_EMAIL` | `demo@asesor.ia` | Identity used until auth exists |
| `CORS_ORIGINS` | `*` | Comma-separated allowed origins |

> **Model correction.** `gemini-1.5-flash` was retired by Google. The default is
> now `gemini-flash-latest`; set `GEMINI_MODEL` if you need a pinned version.

## API

| Method | Path | Purpose |
| --- | --- | --- |
| `POST` | `/api/v1/skin/analyze` | Facial diagnosis from a selfie (`file`) |
| `POST` | `/api/v1/skin/compare-progress` | Day 1 vs. today (`baseline_file`, `current_file`, `days_elapsed`) |
| `POST` | `/api/v1/inci/scan` | OCR label + conflict audit (`file`) |
| `POST` | `/api/v1/routine/checkin` | Save AM/PM checklist |
| `GET` | `/api/v1/routine/today?date=YYYY-MM-DD` | Checklist state + streak |
| `GET` | `/api/v1/users/me` | Demo user + skin profile |
| `GET` | `/api/v1/products` | Active routine products |
| `POST` | `/api/v1/products` | Register a product for future INCI audits |
| `GET` | `/api/v1/skin/history` | Evolution log with image URLs |
| `GET` | `/health` | Liveness + whether Gemini is configured |

Error contract: `{"detail": "...", "code": "..."}`.

- `503 ai_unavailable` — missing/invalid `GEMINI_API_KEY` or provider failure
- `422 unusable_image` — no face detected, or unreadable INCI label
- `400 domain_error` — invalid routine step, bad upload, etc.

Example:

```bash
curl -X POST http://localhost:8000/api/v1/skin/analyze \
  -F "file=@selfie.jpg"
```

## Mobile app

```powershell
cd mobile
flutter pub get

# Web (Chrome): localhost is the host machine
flutter run -d chrome

# Android emulator: the app picks 10.0.2.2 automatically
flutter run
```

`AppConfig` resolves the base URL per platform, so `--dart-define` is only
needed when the API is not on the same machine. An explicit
`--dart-define=API_BASE_URL=...` always wins over the platform default, and
`flutter run` must be restarted (not hot-reloaded) for a new value to apply.

For a **physical Android device** on the same Wi-Fi, use the machine's LAN IP:

```powershell
flutter run --dart-define=API_BASE_URL=http://192.168.1.20:8000
```

Or forward the port over USB and keep `localhost`:

```bash
adb reverse tcp:8000 tcp:8000
flutter run --dart-define=API_BASE_URL=http://localhost:8000
```

The Android manifest already allows cleartext HTTP for local development;
remove `android:usesCleartextTraffic="true"` before shipping over HTTPS.

### What the app does

- **Home** — greeting, stored skin profile, AM/PM checklist with live streak,
  shortcuts to the three tools.
- **Diagnóstico facial** — live camera with an oval guide and a client-side
  luminance meter. The photo goes to Gemini; the result shows skin type,
  hydration, undertone, detected issues, routine recommendations, product
  suggestions and the mandatory disclaimer.
- **Mi progreso** — stores the Day 1 photo on-device, then compares it with a
  new capture through the multimodal endpoint. Before/after slider, progress
  percentage, hydration and texture deltas, routine adjustments.
- **Auditar INCI** — captures the label, shows key ingredients and conflicts
  against the active routine, offers a safe alternative and lets the user add
  the scanned product so future audits know about it.

### Mobile architecture

`lib/services/asesor_api.dart` is the typed facade over the four required
endpoints plus the supporting ones. Controllers are `ChangeNotifier`s provided
at the root with `provider`:

- `UserController`, `SkinController`, `ProgressController`,
  `InciController`, `RoutineController`

The checklist is optimistic and serialized per period, so fast taps cannot
overwrite each other. The light meter reads the mean luma of the camera preview
stream (`YUV420` on Android, `BGRA` on iOS) and warns before spending a request.

## Tests

Backend (Windows virtualenv):

```powershell
cd backend
.venv\Scripts\python.exe -m pytest
.venv\Scripts\python.exe -m ruff check .
```

Mobile:

```powershell
cd mobile
flutter analyze
flutter test
flutter build apk --debug
```

Current state: **25 backend tests**, **7 Flutter tests**, `flutter analyze`
clean and a debug APK building successfully.

## Privacy

- Photos are stored on the device for the baseline; they are sent to the API
  only when the user runs an analysis or comparison.
- The server stores uploaded images under `backend/data/storage` to power
  `/skin/history`. Delete that folder (and the DB rows) to purge them.
- Phase 1 has no authentication and uses a demo user.
- The output is cosmetic guidance, not a medical diagnosis; every AI response
  carries a disclaimer.

## Phase 2 slots

`SkinProfile` already persists `colorimetry_season`, `body_shape` and
`style_preference`, and the Flutter `SkinProfile` model exposes them, so the
outfit/style module can reuse the same tables and models without a migration.

## Troubleshooting

| Symptom | Fix |
| --- | --- |
| `503 ai_unavailable` | Set `GEMINI_API_KEY` in `backend/.env` and restart |
| `422 unusable_image` | Better light, no makeup, full face in frame, or a sharper label |
| App shows connection error | Check `API_BASE_URL`, that the API runs on `0.0.0.0:8000`, and the firewall |
| Emulator cannot reach the API | Use `10.0.2.2`, not `localhost` |
| Browser shows `ERR_CONNECTION_TIMED_OUT` on `10.0.2.2:8000` | You are running Flutter **web**, where `10.0.2.2` is not the host. Run `flutter run -d chrome` with no `--dart-define`, or pass `http://localhost:8000` |
| New `--dart-define` value ignored | `flutter run` reads it at build time: stop it and start again; hot reload/restart is not enough |
| Camera permission denied | Grant it in system settings; the app falls back to the gallery |
