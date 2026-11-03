"""Grounded tutor: answers only from lesson JSON plus recent error concepts."""

from src.application import container
from src.application.services import learn as learn_file
from src.domain.enums import AgentNames
from src.domain.models.chat import ChatTurn
from src.domain.models.lesson import Lesson
from src.domain.models.llm import agent_request
from src.infrastructure.llm.contracts.learn import ChatAnswer
from src.infrastructure.llm.prompts.chat import CHAT_PROMPT_CONFIG

MAX_TURNS = 20


def ask(username: str, question: str) -> dict:
    user = container.users().load(username)
    if user is None:
        raise ValueError(f"User '{username}' not found")
    text = (question or "").strip()
    if not text:
        raise ValueError("Ask a question first")

    lessons = _retrieve(text, username)
    excerpts = [_excerpt(lesson) for lesson in lessons]
    request = agent_request(
        name=AgentNames.CHAT_TUTOR,
        system_prompt=CHAT_PROMPT_CONFIG[AgentNames.CHAT_TUTOR],
        stimulus=excerpts or "No lesson excerpts matched.",
        input=text,
        schema=ChatAnswer,
    )
    answer = container.llm().structured(request, ChatAnswer)
    keys = [key for key in answer.lesson_keys if container.content().lesson(key)]
    if not keys:
        keys = [lesson.key for lesson in lessons[:2]]

    user.chat_history.append(ChatTurn(role="user", text=text))
    user.chat_history.append(
        ChatTurn(role="assistant", text=answer.answer_en, lesson_keys=keys),
    )
    user.chat_history = user.chat_history[-MAX_TURNS:]
    container.users().save(user)

    return {
        "answer_en": answer.answer_en,
        "known": answer.known,
        "lesson_keys": keys,
        "lessons": [learn_file.card_dict(container.content().lesson(key)) for key in keys if container.content().lesson(key)],
        "history": [turn.model_dump(mode="json") for turn in user.chat_history],
    }


def history(username: str) -> list[dict]:
    user = container.users().load(username)
    if user is None:
        raise ValueError(f"User '{username}' not found")
    return [turn.model_dump(mode="json") for turn in user.chat_history]


def _retrieve(question: str, username: str) -> list[Lesson]:
    found = container.content().search_lessons(question, limit=3)
    by_key = {lesson.key: lesson for lesson in found}
    for key in learn_file.recent_error_keys(username):
        if key in by_key:
            continue
        lesson = container.content().lesson(key)
        if lesson is not None:
            by_key[key] = lesson
        if len(by_key) >= 4:
            break
    return list(by_key.values())[:4]


def _excerpt(lesson: Lesson) -> dict:
    return {
        "key": lesson.key,
        "title_en": lesson.title_en,
        "when_to_use": lesson.when_to_use,
        "rule": lesson.rule,
        "common_mistake": lesson.common_mistake,
        "examples": [example.model_dump() for example in lesson.examples[:3]],
        "table": lesson.table,
    }
