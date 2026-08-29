
from datetime import datetime

from typing import ClassVar, Optional

from pydantic import BaseModel, Field

from src.domain.enums import Band, Grammar, RelativeLevel, Skill, Tenses, Topics


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

    tenses: dict[Tenses, ComputeStats] = Field(default_factory=dict)
    grammar: dict[Grammar, ComputeStats] = Field(default_factory=dict)
    topics: dict[Topics, ComputeStats] = Field(default_factory=dict)

    @classmethod
    def example_json(cls) -> dict:
        return cls._EXAMPLE.copy()


class SkillProgress(BaseModel):
    """Layer two: how the learner is doing at one skill.

    `relative_level` says whether this skill lags, matches, or leads the
    learner's top-level band, so reading can run ahead of speaking.
    """

    relative_level: RelativeLevel = RelativeLevel.AT
    genuine_attempts: int = 0
    total_attempts: int = 0
    rolling_accuracy: float = 0.0
    last_practised: Optional[datetime] = None
    # Layer three, scoped to this skill.
    concepts: Progress = Field(default_factory=Progress)


class ProgressUpdates(BaseModel):
    id: str
    exercise_id: str
    time: datetime
    score: Progress
    new_progress: Progress
    skill: Optional[Skill] = None
    genuine: bool = True
    accuracy: Optional[float] = None
    band: Optional[Band] = None
    band_change: Optional[str] = None
