from typing import Optional

from pydantic import BaseModel, Field

from src.domain.models.progress import ProgressUpdates, Progress
from src.domain.models.session import ExerciseStorage, SessionStorage


class User(BaseModel):
    name: str
    progress: Progress
    first_time: bool
    current_exercise: Optional[ExerciseStorage] = None
    history: list[SessionStorage] = Field(default_factory=list)
    progress_history: list[ProgressUpdates] = Field(default_factory=list)