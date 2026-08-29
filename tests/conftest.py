import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from datetime import datetime  # noqa: E402

from src.application import container  # noqa: E402
from src.domain.enums import Band, Direction, LengthPreference, WeeklyTime  # noqa: E402
from src.domain.models.profile import PlacementResult, Proficiency, UserGoals  # noqa: E402
from src.domain.models.user import User  # noqa: E402
from src.domain.utils import initialise_progress  # noqa: E402
from src.infrastructure.persistence.json_content import JsonContentRepository  # noqa: E402


class FakeUserRepository:
    """In-memory user store."""

    def __init__(self) -> None:
        self.saved: dict[str, User] = {}

    def load(self, username: str) -> User | None:
        user = self.saved.get(username)
        return user.model_copy(deep=True) if user else None

    def save(self, user: User) -> None:
        self.saved[user.name] = user.model_copy(deep=True)

    def create(self, username: str) -> bool:
        return username not in self.saved

    def seed(
        self,
        username: str,
        band: Band = Band.A2,
        placed: bool = True,
        length: LengthPreference = LengthPreference.STANDARD,
    ) -> User:
        """A user who has finished onboarding, which most flows require."""
        user = User(
            name=username,
            progress=initialise_progress(),
            first_time=False,
            goals=UserGoals(
                direction=Direction.TRAVEL,
                desired_band=Band.B1,
                weekly_time=WeeklyTime.T_1_2H,
                length_preference=length,
            ),
            proficiency=Proficiency(current=band, updated_at=datetime.now()),
            placement=PlacementResult(
                completed=placed,
                mcq_correct=4,
                mcq_total=8,
                assigned_band=band,
                taken_at=datetime.now(),
            ),
        )
        self.save(user)
        return user

    def seed_new(self, username: str) -> User:
        """A brand-new user with no goals and no placement."""
        user = User(name=username, progress=initialise_progress(), first_time=True)
        self.save(user)
        return user


class FakeTtsGateway:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def synthesise(self, text: str, voice: str = "nova") -> str:
        self.calls.append(text)
        return "test-clip"


class FakeSttGateway:
    def __init__(self) -> None:
        self.calls: list[str] = []
        self.transcript = "Hola, estoy bien."

    def transcribe(self, audio_bytes: bytes, filename: str = "speech.webm") -> str:
        self.calls.append(filename)
        return self.transcript


class FakeLlmGateway:
    """Returns canned responses so services run without network calls."""

    def __init__(self) -> None:
        self.text_calls: list = []
        self.structured_calls: list = []
        self.text_response = "Escribe sobre tu ultimo viaje."
        self.structured_responses: dict = {}

    def text(self, request) -> str:
        self.text_calls.append(request)
        return self.text_response

    def structured(self, request, schema):
        self.structured_calls.append((request, schema))
        if schema in self.structured_responses:
            return self.structured_responses[schema]
        raise AssertionError(f"FakeLlmGateway has no canned response for {schema.__name__}")


@pytest.fixture
def fake_users() -> FakeUserRepository:
    return FakeUserRepository()


@pytest.fixture
def fake_llm() -> FakeLlmGateway:
    return FakeLlmGateway()


@pytest.fixture
def real_content() -> JsonContentRepository:
    """The shipped content bank. Exercised for real so the JSON stays valid."""
    return JsonContentRepository()


@pytest.fixture
def fake_tts() -> FakeTtsGateway:
    return FakeTtsGateway()


@pytest.fixture
def fake_stt() -> FakeSttGateway:
    return FakeSttGateway()


@pytest.fixture
def deps(fake_users, fake_llm, real_content, fake_tts, fake_stt):
    """Configure the container with fakes for the duration of one test."""
    bound = container.Deps(
        users=fake_users,
        llm=fake_llm,
        content=real_content,
        tts=fake_tts,
        stt=fake_stt,
    )
    container.configure(bound)
    yield bound
    container._deps = None
