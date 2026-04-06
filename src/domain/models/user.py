from typing import Optional

from pydantic import BaseModel, Field

from src.domain.models.exercise import ExerciseStorage
from src.domain.models.progress import ProgressUpdates, Progress


class User(BaseModel):
    name: str
    progress: Progress
    first_time: bool
    current_exercise: Optional[ExerciseStorage] = None
    exercise_history: list[ExerciseStorage] = Field(default_factory=list)
    progress_history: list[ProgressUpdates] = Field(default_factory=list)