from typing import ClassVar

from pydantic import BaseModel

from src.domain.enums import Grammar, Tenses, Topics


class Edit(BaseModel):
    _EXAMPLE: ClassVar[dict] = {
        "original_text": "Yo fue al mercado.",
        "corrected_text": "Yo fui al mercado.",
        "reason": "Incorrect verb conjugation for first person singular.",
    }

    original_text: str
    corrected_text: str
    reason: str

    @classmethod
    def example_json(cls) -> dict:
        return cls._EXAMPLE.copy()


class TextCorrection(BaseModel):
    _EXAMPLE: ClassVar[dict] = {
        "corrected_version": "Ayer fui al mercado con mi hermana.",
        "tense_errors": {
            "presente_de_indicativo": [Edit._EXAMPLE],
            "preterito_perfecto_simple": [Edit._EXAMPLE],
            "preterito_imperfecto": [Edit._EXAMPLE],
            "futuro_simple": [Edit._EXAMPLE],
            "condicional_simple": [Edit._EXAMPLE],
        },
        "grammar_errors": {
            "gender_agreement": [Edit._EXAMPLE],
            "plurality_agreement": [Edit._EXAMPLE],
            "por_para_usage": [Edit._EXAMPLE],
            "indirect_direct_pronoun_usage": [Edit._EXAMPLE],
            "verb_subject_conjugation": [Edit._EXAMPLE],
        },
        "topic_errors": {
            "travel": [Edit._EXAMPLE],
            "school": [Edit._EXAMPLE],
            "work": [Edit._EXAMPLE],
            "culture": [Edit._EXAMPLE],
            "current_events": [Edit._EXAMPLE],
            "emotions": [Edit._EXAMPLE],
            "relationships": [Edit._EXAMPLE],
        },
        "typos": [Edit._EXAMPLE],
        "other_mistakes": [Edit._EXAMPLE],
    }

    corrected_version: str
    tense_errors: dict[Tenses, list[Edit]]
    grammar_errors: dict[Grammar, list[Edit]]
    topic_errors: dict[Topics, list[Edit]]
    typos: list[Edit]
    other_mistakes: list[Edit]

    @classmethod
    def example_json(cls) -> dict:
        return cls._EXAMPLE.copy()
