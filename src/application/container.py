from dataclasses import dataclass

from src.application.ports import ContentRepository, LlmGateway, UserRepository


@dataclass(frozen=True)
class Deps:
    users: UserRepository
    llm: LlmGateway
    content: ContentRepository


_deps: Deps | None = None


def configure(deps: Deps) -> None:
    global _deps
    _deps = deps


def get() -> Deps:
    if _deps is None:
        raise RuntimeError(
            "Application container is not configured. "
            "The composition root must call configure() before handling requests.",
        )
    return _deps


def users() -> UserRepository:
    return get().users


def llm() -> LlmGateway:
    return get().llm


def content() -> ContentRepository:
    return get().content
