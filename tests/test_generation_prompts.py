"""Generation prompts must describe a real task, not a worksheet template."""

from src.infrastructure.llm.prompts import chat as chat_prompts
from src.infrastructure.llm.prompts import drills as drills_prompts
from src.infrastructure.llm.prompts import listening as listening_prompts
from src.infrastructure.llm.prompts import reading as reading_prompts
from src.infrastructure.llm.prompts import speaking as speaking_prompts
from src.infrastructure.llm.prompts import writing as writing_prompts


def test_writing_prompt_is_not_a_fill_in_the_blank_template():
    text = writing_prompts.w_instruction_system_prompt
    assert "Usa (tenses)" not in text
    assert "asegúrate de usar correctamente (grammar)" not in text
    assert "situándolo en una situación específica" not in text
    assert "never name them" in text.lower() or "must never name them" in text


def test_writing_prompt_asks_for_spanish_paragraphs_not_json():
    text = writing_prompts.w_instruction_system_prompt
    assert "two paragraphs" in text.lower()
    assert "JSON" in text  # forbidden in the output, so the word appears in DO NOT


def test_reading_prompt_follows_level_not_cefr_or_legacy_difficulty():
    text = reading_prompts.r_generation_system_prompt
    assert "Beginner" not in text
    assert "Novice" not in text
    assert "must not exceed B1" not in text
    assert "CEFR" not in text
    assert "level_hint" in text
    assert "0–8" in text or "0-8" in text


def test_writing_prompt_uses_level_not_cefr():
    text = writing_prompts.w_instruction_system_prompt
    assert "CEFR" not in text
    assert "level_hint" in text


def test_reading_prompt_keeps_grammar_implicit():
    text = reading_prompts.r_generation_system_prompt
    assert "Never name them" in text or "do not name them" in text.lower()


def test_drill_prompts_use_0_8_levels_not_cefr():
    blob = "".join(
        getattr(drills_prompts, name)
        for name in dir(drills_prompts)
        if name.endswith("_system_prompt") and isinstance(getattr(drills_prompts, name), str)
    )
    assert "A0/A1" not in blob
    assert "A1/A2" not in blob
    assert "A2/B1" not in blob
    assert "levels 0–2" in blob or "levels 0-2" in blob
    assert "exercise_config.level" in blob


def test_listening_prompt_uses_level_not_cefr():
    text = listening_prompts.LISTENING_GENERATOR_PROMPT
    assert "CEFR" not in text
    assert "level_hint" in text
    assert "never name them" in text.lower()


def test_speaking_prompt_uses_level_not_cefr():
    text = speaking_prompts.SPEAKING_INSTRUCTIONS_PROMPT
    assert "CEFR" not in text
    assert "level_hint" in text
    assert "Spanish only" in text


def test_chat_prompt_is_a_reference_tutor_not_conversation_practice():
    text = chat_prompts.CHAT_TUTOR_PROMPT
    assert "ONLY the lesson excerpts" in text or "only the lesson excerpts" in text.lower()
    assert "not speaking practice" in text.lower() or "not a conversation" in text.lower()
