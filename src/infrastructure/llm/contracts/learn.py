from typing import ClassVar, Optional

from pydantic import BaseModel, Field


class ChatAnswer(BaseModel):
    _EXAMPLE: ClassVar[dict] = {
        "answer_en": "Use the present for habits: 'Trabajo los sábados.'",
        "known": True,
        "lesson_keys": ["presente_de_indicativo"],
    }

    answer_en: str
    known: bool = True
    lesson_keys: list[str] = Field(default_factory=list)

    @classmethod
    def example_json(cls) -> dict:
        return cls._EXAMPLE.copy()


class VocabItem(BaseModel):
    lemma: str
    gloss_en: str
    topic: Optional[str] = None


class VocabExtraction(BaseModel):
    _EXAMPLE: ClassVar[dict] = {
        "items": [
            {"lemma": "mercado", "gloss_en": "market", "topic": "travel"},
            {"lemma": "hermana", "gloss_en": "sister", "topic": "relationships"},
        ]
    }

    items: list[VocabItem] = Field(default_factory=list)

    @classmethod
    def example_json(cls) -> dict:
        return cls._EXAMPLE.copy()
