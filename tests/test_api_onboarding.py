"""Drives the real routers through Starlette's test client."""

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
    monkeypatch.setenv("DOCS_ENABLED", "1")

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


def _auth(client, username="apiuser", new=False):
    res = _login(client, username, new=new)
    assert res.status_code == 200, res.text
    return {"Authorization": f"Bearer {res.json()['token']}"}


def test_login_reports_the_goals_step_for_a_new_user(client):
    res = _login(client)
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["step"] == "goals"
    assert body["username"] == "apiuser"
    assert body["token"]
    assert "user" not in body


def test_login_still_works_if_the_env_key_has_quotes_or_spaces(client, monkeypatch):
    monkeypatch.setenv("ACCESS_KEY", "  'test-key'  ")
    res = _login(client)
    assert res.status_code == 200, res.text


def test_login_does_not_reveal_whether_the_username_exists(client, fake_users):
    fake_users.seed("apiuser")
    missing = _login(client, "nobody", new=False)
    wrong_key = client.post(
        "/user/login",
        json={"username": "apiuser", "key": "nope", "new": False},
    )
    assert missing.status_code == 401
    assert wrong_key.status_code == 401
    assert missing.json()["detail"] == wrong_key.json()["detail"]


def test_private_routes_require_a_session(client, fake_users):
    fake_users.seed("apiuser")
    res = client.post(
        "/exercise/generate",
        json={"username": "apiuser", "type": "writing", "style": "weaknesses"},
    )
    assert res.status_code == 401


def test_session_is_bound_to_the_signed_in_user(client, fake_users):
    fake_users.seed("alice")
    fake_users.seed("bob")
    headers = _auth(client, "alice")
    res = client.post("/chat/history", json={"username": "bob"}, headers=headers)
    assert res.status_code == 200, res.text
    assert res.json()["history"] == []
    assert fake_users.saved["bob"].chat_history == []


def test_exercise_request_rejects_a_client_difficulty(client, fake_users):
    """Difficulty is server-owned, so an extra field must not change anything."""
    fake_users.seed("apiuser", band=Band.A1)
    headers = _auth(client)

    res = client.post(
        "/exercise/generate",
        json={
            "username": "apiuser",
            "type": "writing",
            "style": "weaknesses",
            "difficulty": "intermediate",
        },
        headers=headers,
    )
    assert res.status_code == 200, res.text
    assert res.json()["exercise"]["band"] == Band.A1.value


def test_exercises_are_blocked_before_placement(client, fake_users):
    fake_users.seed_new("apiuser")
    headers = _auth(client)
    res = client.post(
        "/exercise/generate",
        json={"username": "apiuser", "type": "writing", "style": "weaknesses"},
        headers=headers,
    )
    assert res.status_code == 400
    assert "placement" in res.json()["detail"].lower()


def test_full_onboarding_over_http(client, fake_users, fake_llm):
    fake_users.seed_new("apiuser")
    headers = _auth(client)

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
        headers=headers,
    )
    assert goals.status_code == 200, goals.text
    assert goals.json()["step"] == "placement"
    assert "user" not in goals.json()

    form = client.get("/onboarding/placement", headers=headers)
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
        headers=headers,
    )
    assert submitted.status_code == 200, submitted.text
    body = submitted.json()
    assert body["assigned_band"] in {band.value for band in Band}
    assert body["assigned_level"] in range(0, 9)
    assert "A1" not in body["gloss"] and "B1" not in body["gloss"]
    assert body["plan"]["target_level"] == 6
    assert body["plan"]["target_band"] == "B1"

    again = client.post(
        "/onboarding/placement",
        json={"username": "apiuser", "submission": {"mcq_answers": {}, "writing_response": "", "reading_answers": []}},
        headers=headers,
    )
    assert again.status_code == 400
    assert "already" in again.json()["detail"].lower()

    status = client.get("/onboarding/status", headers=headers)
    assert status.status_code == 200
    assert status.json()["step"] == "ready"

    recs = client.post("/exercise/recommend", json={"username": "apiuser"}, headers=headers)
    assert recs.status_code == 200, recs.text
    body = recs.json()
    assert len(body["daily"]) == 4
    assert len(body["cards"]) == 4

    started = client.post(
        "/exercise/generate",
        json={"username": "apiuser", "type": "writing", "style": "weaknesses"},
        headers=headers,
    )
    assert started.status_code == 200, started.text


def test_openapi_no_longer_advertises_difficulty(client):
    schema = client.get("/openapi.json").json()
    request_schema = schema["components"]["schemas"]["ExerciseRequest"]
    assert "difficulty" not in request_schema["properties"]


def test_progress_overview_is_served_with_english_labels(client, fake_users):
    fake_users.seed("apiuser", band=Band.A2)
    headers = _auth(client)

    res = client.post("/progress/generate", json={"username": "apiuser"}, headers=headers)
    assert res.status_code == 200, res.text

    overview = res.json()["overview"]
    assert overview["overall"]["band"] == Band.A2.value
    assert overview["overall"]["gloss"]
    assert overview["overall"]["attempts_until_review"] > 0

    labels = [row["label"] for row in overview["tenses"]]
    assert "Present tense" in labels
    assert all("_" not in label for label in labels)

    assert overview["skills"] == []
    assert overview["genuine_attempts"] == 0


def test_recommend_returns_four_daily_slots(client, fake_users):
    fake_users.seed("apiuser", band=Band.A2)
    headers = _auth(client)

    res = client.post("/exercise/recommend", json={"username": "apiuser"}, headers=headers)
    assert res.status_code == 200, res.text

    body = res.json()
    daily = body["daily"]
    assert len(daily) == 4
    assert [slot["type"] for slot in daily] == ["writing", "reading", "listening", "speaking"]
    assert daily[1]["focus"]["focus_tenses"] == ["futuro_simple"]
    assert daily[2]["focus"]["focus_topics"] == ["travel"]
    assert all(slot["reason_en"] for slot in daily)
    assert body["remaining"] == 4
    assert body["complete"] is False
    cards = body["cards"]
    assert len(cards) == 4
    assert cards[0]["type"] == "writing"


def test_a_recommend_card_starts_the_existing_generate_pipeline(client, fake_users):
    fake_users.seed("apiuser", band=Band.A2)
    headers = _auth(client)
    cards = client.post("/exercise/recommend", json={"username": "apiuser"}, headers=headers).json()["cards"]
    writing = cards[0]

    res = client.post(
        "/exercise/generate",
        json={
            "username": "apiuser",
            "type": writing["type"],
            "style": writing["style"],
            "preferences": writing["focus"],
        },
        headers=headers,
    )
    assert res.status_code == 200, res.text
    exercise = res.json()["exercise"]
    assert exercise["exercise_type"] == writing["type"]
    assert exercise["areas_of_focus"]["focus_tenses"] == writing["focus"]["focus_tenses"]


def test_recommend_requires_placement(client, fake_users):
    fake_users.seed("apiuser", band=Band.A2, placed=False)
    headers = _auth(client)
    res = client.post("/exercise/recommend", json={"username": "apiuser"}, headers=headers)
    assert res.status_code == 400
    assert "placement" in res.json()["detail"].lower()
