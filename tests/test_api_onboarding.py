"""Drives the real routers through Starlette's test client."""

import os

import pytest
from fastapi.testclient import TestClient

from src.api.main import create_app
from src.application import container
from src.domain.enums import Band
from src.infrastructure.llm.contracts.placement import PlacementAssessment

pytestmark = pytest.mark.usefixtures("deps")


@pytest.fixture
def client(deps, fake_users, monkeypatch, tmp_path):
    monkeypatch.setenv("ACCESS_KEY", "test-key")
    monkeypatch.setenv("USERDATA_DIR", str(tmp_path))

    app = create_app()
    # create_app() installs the real adapters; put the fakes back.
    container.configure(deps)
    with TestClient(app) as c:
        yield c


def _login(client, username="apiuser", new=True):
    return client.post(
        "/user/login",
        json={"username": username, "key": "test-key", "new": new},
    )


def test_login_reports_the_goals_step_for_a_new_user(client):
    res = _login(client)
    assert res.status_code == 200, res.text
    assert res.json()["step"] == "goals"


def test_exercise_request_rejects_a_client_difficulty(client, fake_users):
    """Difficulty is server-owned, so an extra field must not change anything."""
    fake_users.seed("apiuser", band=Band.A1)

    res = client.post(
        "/exercise/generate",
        json={
            "username": "apiuser",
            "type": "writing",
            "style": "weaknesses",
            "difficulty": "intermediate",
        },
    )
    assert res.status_code == 200, res.text
    assert res.json()["exercise"]["band"] == Band.A1.value


def test_exercises_are_blocked_before_placement(client, fake_users):
    fake_users.seed_new("apiuser")
    res = client.post(
        "/exercise/generate",
        json={"username": "apiuser", "type": "writing", "style": "weaknesses"},
    )
    assert res.status_code == 400
    assert "placement" in res.json()["detail"].lower()


def test_full_onboarding_over_http(client, fake_users, fake_llm):
    fake_users.seed_new("apiuser")

    goals = client.post(
        "/onboarding/goals",
        json={
            "username": "apiuser",
            "goals": {
                "direction": "travel",
                "desired_band": "B1",
                "weekly_time": "1-2h",
                "length_preference": "standard",
            },
        },
    )
    assert goals.status_code == 200, goals.text
    assert goals.json()["step"] == "placement"

    form = client.get("/onboarding/placement")
    assert form.status_code == 200, form.text
    assert "answer" not in form.text

    fake_llm.structured_responses = {
        PlacementAssessment: PlacementAssessment(
            writing_signal=0.5,
            reading_signal=0.6,
            notes_en="Solid present tense.",
        ),
    }

    mcq = form.json()["form"]["mcq"]
    submitted = client.post(
        "/onboarding/placement",
        json={
            "username": "apiuser",
            "submission": {
                "mcq_answers": {item["id"]: item["options"][0] for item in mcq},
                "writing_response": "Fui al mercado con mi hermana el sabado.",
                "reading_answers": ["En un pueblo.", "Compra pan.", "Van a las montanas."],
            },
        },
    )
    assert submitted.status_code == 200, submitted.text
    body = submitted.json()
    assert body["assigned_band"] in {band.value for band in Band}
    assert body["plan"]["target_band"] == "B1"

    status = client.get("/onboarding/status", params={"username": "apiuser"})
    assert status.status_code == 200
    assert status.json()["step"] == "ready"

    # Now that placement is done, exercises unlock.
    started = client.post(
        "/exercise/generate",
        json={"username": "apiuser", "type": "writing", "style": "weaknesses"},
    )
    assert started.status_code == 200, started.text


def test_openapi_no_longer_advertises_difficulty(client):
    schema = client.get("/openapi.json").json()
    request_schema = schema["components"]["schemas"]["ExerciseRequest"]
    assert "difficulty" not in request_schema["properties"]


def test_progress_overview_is_served_with_english_labels(client, fake_users):
    fake_users.seed("apiuser", band=Band.A2)

    res = client.post("/progress/generate", json={"username": "apiuser"})
    assert res.status_code == 200, res.text

    overview = res.json()["overview"]
    assert overview["overall"]["band"] == Band.A2.value
    assert overview["overall"]["gloss"]
    assert overview["overall"]["attempts_until_review"] > 0

    labels = [row["label"] for row in overview["tenses"]]
    assert "Present tense" in labels
    assert all("_" not in label for label in labels)

    # A learner who has done nothing yet has no per-skill rows.
    assert overview["skills"] == []
    assert overview["genuine_attempts"] == 0
