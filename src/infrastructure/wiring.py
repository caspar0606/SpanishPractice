"""Concrete adapters for the application ports.

These classes satisfy the protocols in `src/application/ports.py` structurally,
so nothing here imports the application layer. The composition root
(`src/api/main.py`) assembles them into the container at startup.
"""

from typing import TypeVar

from pydantic import BaseModel

from src.domain.models.llm import AgentRequest
from src.domain.models.user import User
from src.infrastructure.llm.harness import agent_run, message_text, response_format
from src.infrastructure.persistence.file_storage import (
    create_new_user_file,
    load_user_state,
    save_user_state,
)
from src.infrastructure.persistence.json_content import JsonContentRepository

T = TypeVar("T", bound=BaseModel)


class FileUserRepository:
    """JSON-file backed user store."""

    def load(self, username: str) -> User | None:
        return load_user_state(username)

    def save(self, user: User) -> None:
        save_user_state(user)

    def create(self, username: str) -> bool:
        return create_new_user_file(username) == 0


class LangChainLlmGateway:
    """LangChain agent runtime."""

    def text(self, request: AgentRequest) -> str:
        response = agent_run(request)
        return message_text(response["messages"][-1].content)

    def structured(self, request: AgentRequest, schema: type[T]) -> T:
        return response_format(request, schema)


def build_user_repository() -> FileUserRepository:
    return FileUserRepository()


def build_llm_gateway() -> LangChainLlmGateway:
    return LangChainLlmGateway()


def build_content_repository() -> JsonContentRepository:
    return JsonContentRepository()
