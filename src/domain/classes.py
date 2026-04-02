from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from src.domain.enums import Tenses, Grammar, Topics, DifficultyLevels, ExerciseTypes


class ComputeStats(BaseModel):
    total_attempts: float = 0
    correct_attempts: float = 0

class Progress(BaseModel):
    tenses: dict[Tenses, ComputeStats]
    grammar: dict[Grammar, ComputeStats]
    topics: dict[Topics, ComputeStats]


class Exercise(BaseModel):
    exercise_type: Optional[ExerciseTypes] = None
    difficulty_level: DifficultyLevels
    focus_tenses: Optional[list[Tenses]] = None
    focus_grammar: Optional[list[Grammar]] = None
    focus_topics: Optional[list[Topics]] = None
    start_time: datetime
    end_time: Optional[datetime] = None

class User(BaseModel):
    name: str
    progress: Progress
    first_time: bool
    history: Optional[list["CurrentSession"]] = None
    progress_history: Optional[list[Progress]] = None

class CurrentSession(BaseModel):
    user: User
    current_exercise: Exercise
    history: list[Exercise] = []



    