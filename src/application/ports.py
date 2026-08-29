from typing import Protocol, TypeVar

from pydantic import BaseModel

from src.domain.models.lesson import Lesson
from src.domain.models.llm import AgentRequest
from src.domain.models.user import User

T = TypeVar("T", bound=BaseModel)


class UserRepository(Protocol):
    """Persistence for user records."""

    def load(self, username: str) -> User | None: ...

    def save(self, user: User) -> None: ...

    def create(self, username: str) -> bool:
        """Reserve storage for a new user. False if the username is taken."""
        ...


class LlmGateway(Protocol):
    """Access to the LLM agent runtime.

    Both methods return plain values, so callers never see the underlying
    agent framework's response shape.
    """

    def text(self, request: AgentRequest) -> str: ...

    def structured(self, request: AgentRequest, schema: type[T]) -> T: ...


class ContentRepository(Protocol):
    """Read-only access to the curated JSON content under `content/`."""

    def placement_bank(self) -> dict: ...

    def curriculum(self) -> dict: ...

    def lessons(self) -> list[Lesson]: ...

    def lesson(self, key: str) -> Lesson | None: ...

    def search_lessons(self, query: str, limit: int = 4) -> list[Lesson]: ...


class TtsGateway(Protocol):
    """Text to speech. Returns a clip id the API can serve as audio."""

    def synthesise(self, text: str, voice: str = "nova") -> str: ...


class SttGateway(Protocol):
    """Speech to text."""

    def transcribe(self, audio_bytes: bytes, filename: str = "speech.webm") -> str: ...
