from typing import ClassVar

from pydantic import BaseModel, Field

from src.infrastructure.llm.contracts.text_correction import TextCorrection


class ReadingGeneration(BaseModel):
    _EXAMPLE: ClassVar[dict] = {
        "passage": "Ayer fui al mercado con mi hermana. Compramos fruta y hablamos con el vendedor.",
        "questions": [
            "¿Con quién fue la persona al mercado?",
            "¿Qué compraron en el mercado?",
            "¿Con quién hablaron?",
            "¿Dónde ocurrió la acción?",
            "¿Qué hicieron además de comprar fruta?",
        ],
    }

    passage: str
    questions: list[str] = Field(min_length=5, max_length=5)

    @classmethod
    def example_json(cls) -> dict:
        return cls._EXAMPLE.copy()


class TextCorrections(BaseModel):
    _EXAMPLE: ClassVar[dict] = {
        "corrections": [
            {
                "corrected_version": "Ayer fui al mercado con mi hermana.",
                "tense_errors": {},
                "grammar_errors": {},
                "topic_errors": {},
                "typos": [],
                "other_mistakes": [],
            }
        ]
    }

    corrections: list[TextCorrection]

    @classmethod
    def example_json(cls) -> dict:
        return cls._EXAMPLE.copy()


class QuestionMarking(BaseModel):
    _EXAMPLE: ClassVar[dict] = {
        "individual_questions": [
            "Correct: they went with their sister.",
            "Correct: they bought fruit.",
            "Correct: they spoke with the vendor.",
            "Mostly correct: it was at the market.",
            "Partial: mentions buying but not the conversation.",
        ],
        "general_feedback": "topic_score: 0.75. You understood the main ideas, but a couple answers lacked detail.",
    }

    individual_questions: list[str]
    general_feedback: str

    @classmethod
    def example_json(cls) -> dict:
        return cls._EXAMPLE.copy()
