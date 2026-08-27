from datetime import datetime
from typing import Any, ClassVar, Optional

from pydantic import BaseModel, field_validator

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
