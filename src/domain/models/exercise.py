from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel

from src.domain.enums import DifficultyLevels, ExerciseTypes, Grammar, Tenses, Topics
from src.domain.models.progress import Progress


class AreasOfFocus(BaseModel):
    focus_tenses: Optional[list[Tenses]] = None
    focus_grammar: Optional[list[Grammar]] = None
    focus_topics: Optional[list[Topics]] = None

class ExerciseConfig(BaseModel):
    difficulty: DifficultyLevels
    word_count: int

class Exercise(BaseModel):
    id: str
    exercise_type: ExerciseTypes
    difficulty_level: DifficultyLevels
    areas_of_focus: AreasOfFocus
    start_time: datetime
    end_time: Optional[datetime] = None

class ExerciseContext(BaseModel):
    areas_of_focus: AreasOfFocus
    exercise_config: ExerciseConfig 

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


