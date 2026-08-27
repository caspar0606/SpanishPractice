from typing import Optional

from pydantic import BaseModel, Field

from src.domain.models.exercise import ExerciseStorage
from src.domain.models.profile import PlacementResult, Proficiency, UserGoals
from src.domain.models.progress import Progress, ProgressUpdates

SCHEMA_VERSION = 2


class User(BaseModel):
    schema_version: int = SCHEMA_VERSION
    name: str
    progress: Progress
    first_time: bool
    goals: Optional[UserGoals] = None
    proficiency: Proficiency = Field(default_factory=Proficiency)
    placement: PlacementResult = Field(default_factory=PlacementResult)
    current_exercise: Optional[ExerciseStorage] = None
    exercise_history: list[ExerciseStorage] = Field(default_factory=list)
    progress_history: list[ProgressUpdates] = Field(default_factory=list)
