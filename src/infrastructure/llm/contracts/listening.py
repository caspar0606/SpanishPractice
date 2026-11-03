from typing import ClassVar

from pydantic import BaseModel, Field


class DialogueTurn(BaseModel):
    speaker: str
    line: str


class ListeningGeneration(BaseModel):
    _EXAMPLE: ClassVar[dict] = {
        "dialogue": [
            {"speaker": "Ana", "line": "Hola, ¿vas al mercado?"},
            {"speaker": "Luis", "line": "Sí, necesito pan y fruta."},
            {"speaker": "Ana", "line": "Yo también. ¿Caminamos juntos?"},
            {"speaker": "Luis", "line": "Vale, salimos en cinco minutos."},
        ],
        "questions": [
            "¿Adónde va Luis?",
            "¿Qué necesita comprar?",
            "¿Van juntos?",
        ],
    }

    dialogue: list[DialogueTurn] = Field(min_length=3, max_length=8)
    questions: list[str] = Field(min_length=2, max_length=3)

    @classmethod
    def example_json(cls) -> dict:
        return cls._EXAMPLE.copy()
