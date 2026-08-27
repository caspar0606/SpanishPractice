from datetime import datetime
from typing import Any, ClassVar, Optional

from pydantic import BaseModel, ConfigDict, field_validator

from src.domain.enums import DifficultyLevels, ExerciseTypes, Grammar, Tenses, Topics, is_category_sentinel
from src.domain.models.progress import Progress


class AreasOfFocus(BaseModel):
    _EXAMPLE: ClassVar[dict] = {
        "focus_tenses": None,
        "focus_grammar": None,
        "focus_topics": ["travel"],
    }
    model_config = ConfigDict(json_schema_extra={"example": _EXAMPLE})

    focus_tenses: Optional[list[Tenses]] = None
    focus_grammar: Optional[list[Grammar]] = None
    focus_topics: Optional[list[Topics]] = None

    # A category sentinel names the category, not something a learner can practise, so it
    # is not a valid focus even when a client sends one. Dropping it keeps the downstream
    # progress lookups (which only ever hold practisable areas) from raising.
    @field_validator("focus_tenses", "focus_grammar", "focus_topics", mode="after")
    @classmethod
    def drop_category_sentinels(cls, areas: Optional[list]) -> Optional[list]:
        if areas is None:
            return None
        return [area for area in areas if not is_category_sentinel(area)]

    @classmethod
    def example_json(cls) -> dict:
        return cls._EXAMPLE.copy()

class ExerciseConfig(BaseModel):
    _EXAMPLE: ClassVar[dict] = {"difficulty": "beginner", "word_count": 160}
    model_config = ConfigDict(json_schema_extra={"example": _EXAMPLE})

    difficulty: DifficultyLevels
    word_count: int

    @classmethod
    def example_json(cls) -> dict:
        return cls._EXAMPLE.copy()

class Exercise(BaseModel):
    id: str
    exercise_type: ExerciseTypes
    difficulty_level: DifficultyLevels
    areas_of_focus: AreasOfFocus
    start_time: datetime
    end_time: Optional[datetime] = None

class ExerciseContext(BaseModel):
    _EXAMPLE: ClassVar[dict] = {
        "areas_of_focus": AreasOfFocus._EXAMPLE,
        "exercise_config": ExerciseConfig._EXAMPLE,
    }
    model_config = ConfigDict(json_schema_extra={"example": _EXAMPLE})

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


