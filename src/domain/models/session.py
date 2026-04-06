from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel

from src.domain.enums import ExerciseTypes
from src.domain.models.exercise import AreasOfFocus, Exercise, ExerciseStorage
from src.domain.models.progress import ProgressUpdates, Progress
from src.domain.models.user import User


class Session(BaseModel):
    id: str
    user: User
    start_time: datetime
    current_exercise: Exercise
    exercise_history: list[ExerciseStorage]
    progress_history: list[ProgressUpdates]

class SessionStorage(BaseModel):
    id: str
    start_time: datetime
    end_time: datetime
    exercises: Optional[list[ExerciseStorage]]
    progress_updates: Optional[list[ProgressUpdates]]