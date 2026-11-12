"""Android flow and privacy regressions using synthetic images only."""

from sqlalchemy import select

from tests.conftest import make_jpeg, upload


def other_account(client):
    data = {
        "email": "other@example.org",
        "full_name": "Other User",
        "password": "other-password-123",
    }
    assert client.post("/api/v1/auth/register", json=data).status_code == 201
    token = client.post("/api/v1/auth/login", json=data).json()["access_token"]
    return {"Authorization": "Bearer " + token}


def test_personal_endpoints_require_session(client):
    for path in [
        "/users/me",
        "/products",
        "/photos",
        "/consents",
        "/routine/today",
        "/skin/history",
        "/analysis/history",
    ]:
        assert client.get("/api/v1" + path, headers={"Authorization": ""}).status_code == 401, path
    assert (
        client.post(
            "/api/v1/skin/analyze",
            files=upload("x.jpg", make_jpeg()),
            headers={"Authorization": ""},
        ).status_code
        == 401
    )


def test_photo_requires_service_consent_even_when_training_granted(client, storage_dir):
    headers = other_account(client)
    client.post(
        "/api/v1/consents", headers=headers, json={"consent_type": "training", "granted": True}
    )
    response = client.post(
        "/api/v1/photos",
        headers=headers,
        data={"photo_type": "front"},
        files=upload("photo.jpg", make_jpeg()),
    )
    assert response.status_code == 403
    assert not list(storage_dir.rglob("*.jpg"))


def test_photos_decode_bytes_and_reject_path_components(client, storage_dir):
    assert (
        client.post(
            "/api/v1/photos", data={"photo_type": "front"}, files=upload("bad.jpg", b"not an image")
        ).status_code
        == 422
    )
    assert (
        client.post(
            "/api/v1/photos",
            data={"photo_type": "../outside"},
            files=upload("good.jpg", make_jpeg()),
        ).status_code
        == 422
    )
    assert not list(storage_dir.rglob("*.jpg"))


def test_photo_is_private_and_delete_removes_disk_file(client, storage_dir):
    response = client.post(
        "/api/v1/photos", data={"photo_type": "front"}, files=upload("private.jpg", make_jpeg())
    )
    assert response.status_code == 201
    photo_id = response.json()["photo_id"]
    path = f"/api/v1/photos/{photo_id}/content"
    assert client.get(path).status_code == 200
    assert client.get(path).headers["cache-control"] == "no-store"
    assert client.get(path, headers={"Authorization": ""}).status_code == 401
    other = other_account(client)
    assert client.get(path, headers=other).status_code == 404
    assert client.delete(f"/api/v1/photos/{photo_id}", headers=other).status_code == 404
    assert "storage_path" not in client.get("/api/v1/photos").json()[0]
    assert client.delete(f"/api/v1/photos/{photo_id}").status_code == 204
    assert not list(storage_dir.rglob("*.jpg"))
    assert client.get(path).status_code == 404


def test_legacy_media_cannot_be_read_by_another_user(client):
    client.post("/api/v1/skin/analyze", files=upload("x.jpg", make_jpeg()))
    path = client.get("/api/v1/skin/history").json()["items"][0]["image_url"]
    assert client.get(path).status_code == 200
    assert client.get(path, headers={"Authorization": ""}).status_code == 401
    assert client.get(path, headers=other_account(client)).status_code == 404


def test_withdrawing_service_blocks_upload_and_analysis(client):
    client.post("/api/v1/consents", json={"consent_type": "service", "granted": False})
    assert (
        client.post(
            "/api/v1/photos", data={"photo_type": "front"}, files=upload("x.jpg", make_jpeg())
        ).status_code
        == 403
    )
    assert (
        client.post("/api/v1/skin/analyze", files=upload("x.jpg", make_jpeg())).status_code == 403
    )


def test_consent_regrant_has_auditable_history(client):
    from app.core.database import get_session_factory
    from app.models.consent_event import ConsentEvent

    for granted in [False, True, False]:
        result = client.post(
            "/api/v1/consents", json={"consent_type": "training", "granted": granted}
        )
        assert result.status_code == 201
        if granted:
            assert result.json()["granted_at"] is not None
            assert result.json()["withdrawn_at"] is None
    assert client.get("/api/v1/consents/training").json() == {"granted": False}
    with get_session_factory()() as db:
        assert (
            len(
                db.scalars(
                    select(ConsentEvent).where(ConsentEvent.consent_type == "training")
                ).all()
            )
            == 3
        )


def test_android_questionnaire_to_routines_without_photos_or_training(client):
    client.post("/api/v1/consents", json={"consent_type": "service", "granted": False})
    client.post("/api/v1/consents", json={"consent_type": "training", "granted": False})
    assert (
        client.post(
            "/api/v1/questionnaires",
            json={
                "answers": [
                    {"question_key": "skin_feeling", "answer_value": "Mixta"},
                    {"question_key": "irritates_easily", "answer_value": "No estoy seguro"},
                    {"question_key": "time", "answer_value": "Menos de 5 minutos"},
                ]
            },
        ).status_code
        == 201
    )
    assessment = client.post("/api/v1/skin-profile/build").json()
    assert assessment["perceived_skin_type"] == "Mixta"
    assert assessment["sensitivity"] is None
    assert assessment["data_source"] == "questionnaire"
    for kind in ["morning", "night"]:
        result = client.post(f"/api/v1/recommendations?routine_type={kind}")
        assert result.status_code == 201
        assert result.json()["generated_from"] == "questionnaire_demo_rules_v1"
        assert all(s["step"] != "treatment" for s in result.json()["steps"])


def test_analysis_validates_ownership_and_history_route(client):
    photo_id = client.post(
        "/api/v1/photos", data={"photo_type": "front"}, files=upload("x.jpg", make_jpeg())
    ).json()["photo_id"]
    result = client.post("/api/v1/analysis", json={"photo_ids": [photo_id]})
    assert result.status_code == 201
    assert result.json()["confidence"] is None
    assert all(value is None for value in result.json()["observations"].values())
    history = client.get("/api/v1/analysis/history")
    assert history.status_code == 200
    assert len(history.json()) == 1
    other = other_account(client)
    client.post(
        "/api/v1/consents", headers=other, json={"consent_type": "service", "granted": True}
    )
    assert (
        client.post("/api/v1/analysis", headers=other, json={"photo_ids": [photo_id]}).status_code
        == 404
    )
    assert client.get("/api/v1/analysis/history", headers=other).json() == []


def test_bad_product_and_routine_return_domain_errors(client):
    assert client.get("/api/v1/catalog/products/missing").status_code == 404
    assert client.post("/api/v1/recommendations?routine_type=bad").status_code == 400
    assert client.post("/api/v1/recommendations?routine_type=morning").status_code == 409


def test_external_ai_disabled_by_default(client, monkeypatch, fake_gemini):
    from app.core.config import Settings, get_settings

    monkeypatch.delenv("ENABLE_EXPERIMENTAL_AI")
    assert Settings(_env_file=None).enable_experimental_ai is False
    monkeypatch.setattr(get_settings(), "enable_experimental_ai", False)
    assert (
        client.post("/api/v1/skin/analyze", files=upload("x.jpg", make_jpeg())).status_code == 503
    )
    assert fake_gemini.count("analyze_skin") == 0


def test_profiles_and_routines_are_isolated(client):
    client.post(
        "/api/v1/questionnaires",
        json={"answers": [{"question_key": "skin_feeling", "answer_value": "Seca"}]},
    )
    client.post("/api/v1/skin-profile/build")
    plan = client.post("/api/v1/recommendations?routine_type=night").json()
    other = other_account(client)
    assert client.get("/api/v1/skin-profile", headers=other).json() is None
    assert client.get("/api/v1/recommendations", headers=other).json() == []
    assert client.get(f"/api/v1/recommendations/{plan['id']}", headers=other).status_code == 404
