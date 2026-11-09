"""End-to-end API tests against a throwaway SQLite database."""

from __future__ import annotations

from app.services.gemini_service import UnusableImage
from tests.conftest import FakeGemini, make_jpeg, upload

ANALYZE_URL = "/api/v1/skin/analyze"
COMPARE_URL = "/api/v1/skin/compare-progress"
INCI_URL = "/api/v1/inci/scan"
CHECKIN_URL = "/api/v1/routine/checkin"
TODAY_URL = "/api/v1/routine/today"


# --------------------------------------------------------------------- health
def test_health_reports_configuration(raw_client) -> None:
    response = raw_client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["gemini_configured"] is False
    assert body["database"] == "sqlite"


def test_openapi_documents_every_required_endpoint(client) -> None:
    paths = client.get("/openapi.json").json()["paths"]
    for path in (ANALYZE_URL, COMPARE_URL, INCI_URL, CHECKIN_URL):
        assert path in paths


# ---------------------------------------------------------------------- users
def test_demo_user_is_created_on_first_read(client) -> None:
    response = client.get("/api/v1/users/me")
    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "demo@asesor.ia"
    assert body["onboarding_completed"] is False
    assert body["skin_profile"] is None


# ---------------------------------------------------------------- skin analyze
def test_analyze_returns_contract_and_persists_evolution(client, fake_gemini, storage_dir) -> None:
    response = client.post(ANALYZE_URL, files=upload("selfie.jpg", make_jpeg()))

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["skin_type"] == "Mixta"
    assert body["hydration_level"] == 62
    assert body["undertone"] == "Cálido"
    assert body["product_suggestions"][0]["affiliate_link"].startswith(
        "https://www.amazon.com/s?k="
    )
    assert "dermatólogo" in body["disclaimer"]

    profile = client.get("/api/v1/users/me").json()
    assert profile["onboarding_completed"] is True
    assert profile["skin_profile"]["skin_type"] == "Mixta"

    history = client.get("/api/v1/skin/history").json()["items"]
    assert len(history) == 1
    assert history[0]["is_baseline"] is True
    assert history[0]["week_number"] == 1

    image_url = history[0]["image_url"]
    assert client.get(image_url).status_code == 200
    assert list(storage_dir.rglob("*.jpg"))


def test_analyze_without_api_key_returns_503(raw_client) -> None:
    response = raw_client.post(ANALYZE_URL, files=upload("selfie.jpg", make_jpeg()))
    assert response.status_code == 503
    assert response.json()["code"] == "ai_unavailable"
    assert "GEMINI_API_KEY" in response.json()["detail"]


def test_analyze_rejects_non_image_payload(client) -> None:
    response = client.post(ANALYZE_URL, files=upload("selfie.jpg", b"this is not an image"))
    assert response.status_code == 422
    assert response.json()["code"] == "invalid_image"


def test_analyze_reports_unusable_face(client, fake_gemini: FakeGemini) -> None:
    fake_gemini.analyze_error = UnusableImage("No se detectó un rostro claro.")
    response = client.post(ANALYZE_URL, files=upload("selfie.jpg", make_jpeg()))
    assert response.status_code == 422
    assert "rostro" in response.json()["detail"]


def test_analyze_unknown_user_returns_404(client) -> None:
    response = client.post(
        ANALYZE_URL, files=upload("selfie.jpg", make_jpeg()), data={"user_id": "deadbeef"}
    )
    assert response.status_code == 404


# -------------------------------------------------------------- skin progress
def test_compare_progress_after_baseline(client, fake_gemini: FakeGemini) -> None:
    assert (
        client.post(ANALYZE_URL, files=upload("day1.jpg", make_jpeg((190, 150, 130)))).status_code
        == 200
    )

    response = client.post(
        COMPARE_URL,
        files={
            "baseline_file": ("day1.jpg", make_jpeg((190, 150, 130)), "image/jpeg"),
            "current_file": ("day30.jpg", make_jpeg((205, 170, 150)), "image/jpeg"),
        },
        data={"days_elapsed": "30"},
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["progress_percentage"] == 28
    assert body["hydration_change"] == "+15% mayor hidratación"
    assert body["recommended_routine_adjustments"] == ["Mantener niacinamida AM"]

    history = client.get("/api/v1/skin/history").json()["items"]
    assert len(history) == 2
    assert history[0]["progress_percentage"] == 28


def test_compare_progress_without_baseline_still_returns_analysis(client) -> None:
    response = client.post(
        COMPARE_URL,
        files={
            "baseline_file": ("w1.jpg", make_jpeg((180, 140, 120)), "image/jpeg"),
            "current_file": ("w4.jpg", make_jpeg((200, 165, 145)), "image/jpeg"),
        },
    )
    assert response.status_code == 200, response.text
    assert response.json()["progress_percentage"] == 28


# ------------------------------------------------------------------ inci scan
def test_inci_scan_detects_conflict_and_caches_ocr(client, fake_gemini: FakeGemini) -> None:
    payload = make_jpeg((240, 240, 235))

    first = client.post(INCI_URL, files=upload("label.jpg", payload))
    second = client.post(INCI_URL, files=upload("label.jpg", payload))

    assert first.status_code == 200, first.text
    body = first.json()
    assert body["has_conflict"] is True
    assert "Retinol" in body["conflict_warning"]
    assert body["safe_alternative"]["affiliate_link"].startswith("https://")
    assert body["key_ingredients"][0] == "Aqua"
    assert second.status_code == 200
    assert fake_gemini.count("read_inci_label") == 1


def test_inci_scan_unreadable_label(client, fake_gemini: FakeGemini) -> None:
    fake_gemini.inci_error = UnusableImage("No se pudo leer la lista INCI.")
    response = client.post(INCI_URL, files=upload("label.jpg", make_jpeg((10, 10, 10))))
    assert response.status_code == 422
    assert "INCI" in response.json()["detail"]


def test_inci_scan_cross_checks_active_routine(client, fake_gemini: FakeGemini) -> None:
    created = client.post(
        "/api/v1/products",
        json={"name": "Retinol Nocturno", "brand": "Test", "key_ingredients": ["Retinol"]},
    )
    assert created.status_code == 201

    fake_gemini.inci_analysis = fake_gemini.inci_analysis.model_copy(
        update={"key_ingredients": ["Aqua", "Salicylic Acid"], "product_name": "BHA Test"}
    )
    response = client.post(INCI_URL, files=upload("bha.jpg", make_jpeg((30, 60, 90))))

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["has_conflict"] is True
    assert "salicílico" in body["conflict_warning"].lower()


def test_product_registry_lists_entries(client) -> None:
    client.post(
        "/api/v1/products",
        json={"name": "Hidratante Ceramidas", "key_ingredients": ["Ceramides"]},
    )
    products = client.get("/api/v1/products").json()
    assert len(products) == 1
    assert products[0]["is_active"] is True


# -------------------------------------------------------------------- routine
def test_routine_checkin_marks_day_and_builds_streak(client) -> None:
    steps = ["limpiador", "vitamina_c", "hidratante", "protector_solar"]
    response = client.post(
        CHECKIN_URL,
        json={
            "log_date": "2026-11-04",
            "period": "AM",
            "completed_steps": steps,
            "notes": "Rutina completa",
        },
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["status"] == "saved"
    assert body["log"]["completed"] is True

    today = client.get(TODAY_URL, params={"date": "2026-11-04"}).json()
    assert today["am"]["completed_steps"] == steps
    assert today["pm"] is None
    assert today["streak_days"] == 1
    assert today["allowed_steps"]["PM"] == ["limpiador", "tratamiento", "hidratante"]


def test_routine_checkin_is_idempotent_per_day_and_period(client) -> None:
    for notes in ("primera", "segunda"):
        response = client.post(
            CHECKIN_URL,
            json={
                "log_date": "2026-11-05",
                "period": "PM",
                "completed_steps": ["limpiador"],
                "notes": notes,
            },
        )
        assert response.status_code == 200

    today = client.get(TODAY_URL, params={"date": "2026-11-05"}).json()
    assert today["pm"]["notes"] == "segunda"
    assert today["pm"]["completed"] is False


def test_routine_checkin_rejects_unknown_step(client) -> None:
    response = client.post(
        CHECKIN_URL,
        json={"period": "AM", "completed_steps": ["mascarilla_de_oro"]},
    )
    assert response.status_code == 422
    assert "mascarilla_de_oro" in response.json()["detail"]
