from datetime import datetime
from typing import Any, ClassVar, Optional

from pydantic import BaseModel, Field, field_validator

from src.domain.enums import Band, ExerciseTypes, Grammar, LengthPreference, Tenses, Topics
from src.domain.models.progress import Progress


class AreasOfFocus(BaseModel):
    _EXAMPLE: ClassVar[dict] = {
        "focus_tenses": None,
        "focus_grammar": None,
        "focus_topics": ["travel"],
    }

    focus_tenses: Optional[list[Tenses]] = None
    focus_grammar: Optional[list[Grammar]] = None
    focus_topics: Optional[list[Topics]] = None

    @field_validator("focus_tenses", "focus_grammar", "focus_topics", mode="before")
    @classmethod
    def _empty_list_to_none(cls, value: Any) -> Any:
        if value == []:
            return None
        return value

    @classmethod
    def example_json(cls) -> dict:
        return cls._EXAMPLE.copy()

class ExerciseConfig(BaseModel):
    _EXAMPLE: ClassVar[dict] = {
        "band": "A2",
        "length": "standard",
        "word_count": 100,
        "question_count": 0,
        "cefr_hint": "A2: common vocabulary, simple past and present, mostly simple sentences.",
    }

    band: Band
    length: LengthPreference = LengthPreference.STANDARD
    word_count: int
    question_count: int = 0
    cefr_hint: str = ""

    @classmethod
    def example_json(cls) -> dict:
        return cls._EXAMPLE.copy()

class Exercise(BaseModel):
    id: str
    exercise_type: ExerciseTypes
    band: Band
    length: LengthPreference = LengthPreference.STANDARD
    areas_of_focus: AreasOfFocus
    start_time: datetime
    end_time: Optional[datetime] = None

class ExerciseContext(BaseModel):
    _EXAMPLE: ClassVar[dict] = {
        "areas_of_focus": AreasOfFocus._EXAMPLE,
        "exercise_config": ExerciseConfig._EXAMPLE,
    }

    areas_of_focus: AreasOfFocus
    exercise_config: ExerciseConfig 

    @classmethod
    def example_json(cls) -> dict:
        return cls._EXAMPLE.copy()

class AttemptMetrics(BaseModel):
    """Observable facts about one submission, used to judge effort.

    `items_total` is zero for prose exercises; it is only set for drills.
    """

    seconds_spent: float = 0.0
    response_words: int = 0
    target_words: int = 0
    items_total: int = 0
    items_answered: int = 0


class GenuineVerdict(BaseModel):
    """Whether an attempt counts as evidence of ability."""

    genuine: bool
    reasons: list[str] = Field(default_factory=list)


class ExerciseStorage(BaseModel):
    id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    type: ExerciseTypes
    areas_of_focus: AreasOfFocus
    exercise_config: ExerciseConfig
    prompt: Optional[Any] = None
    user_response: Optional[Any] = None
    feedback: Optional[Any] = None
    score: Optional[Progress] = None
    metrics: Optional[AttemptMetrics] = None
    genuine: Optional[bool] = None
