"""Chat answers from lesson JSON, not from general knowledge."""

from src.application.services import chat as chat_file
from src.infrastructure.llm.contracts.learn import ChatAnswer


def test_chat_persists_turns_and_points_at_a_lesson(deps, fake_users, fake_llm):
    fake_users.seed("learner")
    fake_llm.structured_responses[ChatAnswer] = ChatAnswer(
        answer_en="Use the present for habits.",
        known=True,
        lesson_keys=["presente_de_indicativo"],
    )

    result = chat_file.ask("learner", "When do I use the present tense?")

    assert result["known"] is True
    assert "presente_de_indicativo" in result["lesson_keys"]
    assert len(result["history"]) == 2
    stored = fake_users.saved["learner"]
    assert stored.chat_history[0].role == "user"
    assert stored.chat_history[1].role == "assistant"


def test_chat_rejects_a_blank_question(deps, fake_users):
    fake_users.seed("learner")
    try:
        chat_file.ask("learner", "  ")
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_lesson_excerpts_stay_as_dicts_on_the_agent_request():
    """Ask passes JSON excerpts. They must not be coerced into bare BaseModel."""
    from src.domain.enums import AgentNames
    from src.domain.models.llm import agent_request
    from src.infrastructure.llm.utils import serialise_for_prompt

    excerpts = [
        {
            "key": "presente_de_indicativo",
            "title_en": "Present tense",
            "when_to_use": ["habits"],
            "table": {"yo": {"present": "hablo"}},
        }
    ]
    request = agent_request(
        name=AgentNames.CHAT_TUTOR,
        system_prompt="tutor",
        stimulus=excerpts,
        input="When do I use the present?",
    )
    assert isinstance(request.stimulus, list)
    assert request.stimulus[0]["key"] == "presente_de_indicativo"
    dumped = serialise_for_prompt(request.stimulus)
    assert "hablo" in dumped
