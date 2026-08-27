
from datetime import datetime

from typing import ClassVar

from pydantic import BaseModel

from src.domain.enums import Grammar, Tenses, Topics


class ComputeStats(BaseModel):
    _EXAMPLE: ClassVar[dict] = {"total_attempts": 3.0, "correct_attempts": 2.0}

    total_attempts: float = 0
    correct_attempts: float = 0

    @classmethod
    def example_json(cls) -> dict:
        return cls._EXAMPLE.copy()

class Progress(BaseModel):
    _EXAMPLE: ClassVar[dict] = {
        "tenses": {
            "presente_de_indicativo": ComputeStats._EXAMPLE,
            "preterito_perfecto_simple": ComputeStats._EXAMPLE,
            "preterito_imperfecto": ComputeStats._EXAMPLE,
            "futuro_simple": ComputeStats._EXAMPLE,
            "condicional_simple": ComputeStats._EXAMPLE,
        },
        "grammar": {
            "gender_agreement": ComputeStats._EXAMPLE,
            "plurality_agreement": ComputeStats._EXAMPLE,
            "por_para_usage": ComputeStats._EXAMPLE,
            "indirect_direct_pronoun_usage": ComputeStats._EXAMPLE,
            "verb_subject_conjugation": ComputeStats._EXAMPLE,
        },
        "topics": {
            "travel": ComputeStats._EXAMPLE,
            "school": ComputeStats._EXAMPLE,
            "work": ComputeStats._EXAMPLE,
            "culture": ComputeStats._EXAMPLE,
            "current_events": ComputeStats._EXAMPLE,
            "emotions": ComputeStats._EXAMPLE,
            "relationships": ComputeStats._EXAMPLE,
        },
    }

    tenses: dict[Tenses, ComputeStats]
    grammar: dict[Grammar, ComputeStats] 
    topics: dict[Topics, ComputeStats]

    @classmethod
    def example_json(cls) -> dict:
        return cls._EXAMPLE.copy()

class ProgressUpdates(BaseModel):
    id: str
    exercise_id: str
    time: datetime
    score: Progress
    new_progress: Progress
