
from datetime import datetime

from typing import ClassVar

from pydantic import BaseModel, ConfigDict, field_validator

from src.domain.enums import Grammar, Tenses, Topics, is_category_sentinel, practice_members


class ComputeStats(BaseModel):
    _EXAMPLE: ClassVar[dict] = {"total_attempts": 3.0, "correct_attempts": 2.0}
    model_config = ConfigDict(json_schema_extra={"example": _EXAMPLE})

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
    model_config = ConfigDict(json_schema_extra={"example": _EXAMPLE})

    tenses: dict[Tenses, ComputeStats]
    grammar: dict[Grammar, ComputeStats] 
    topics: dict[Topics, ComputeStats]

    # Progress is kept total over the practisable areas: every real area is present and no
    # category sentinel ever is. That heals user files written before sentinels were
    # excluded, absorbs the partial dicts a tagging agent returns, and lets weak-area
    # selection assume every area it can choose from has an entry.
    @field_validator("tenses", "grammar", "topics", mode="after")
    @classmethod
    def cover_practisable_areas(cls, scores: dict, info) -> dict:
        enum_cls = {"tenses": Tenses, "grammar": Grammar, "topics": Topics}[info.field_name]
        covered = {area: ComputeStats() for area in practice_members(enum_cls)}
        for area, stats in scores.items():
            if not is_category_sentinel(area):
                covered[area] = stats
        return covered

    @classmethod
    def example_json(cls) -> dict:
        return cls._EXAMPLE.copy()

class ProgressUpdates(BaseModel):
    id: str
    exercise_id: str
    time: datetime
    score: Progress
    new_progress: Progress


