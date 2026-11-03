from dataclasses import dataclass

from src.application.ports import (
    ContentRepository,
    DictionaryGateway,
    LlmGateway,
    SttGateway,
    TtsGateway,
    UserRepository,
)


@dataclass(frozen=True)
class Deps:
    users: UserRepository
    llm: LlmGateway
    content: ContentRepository
    tts: TtsGateway
    stt: SttGateway
    dictionary: DictionaryGateway


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


def tts() -> TtsGateway:
    return get().tts


def stt() -> SttGateway:
    return get().stt


def dictionary() -> DictionaryGateway:
    return get().dictionary
