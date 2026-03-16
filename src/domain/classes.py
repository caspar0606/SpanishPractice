from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from src.domain.enums import Tenses, Grammar, Topics, DifficultyLevels, ExerciseTypes



class ComputeStats(BaseModel):
    total_attempts: int
    correct_attempts: int

class Progress(BaseModel):
    tenses: dict[str, ComputeStats]
    grammar: dict[str, ComputeStats]
    topics: dict[str, ComputeStats]

class User(BaseModel):
    name: str
    progress: Progress
    first_time: bool



class Exercise(BaseModel):
    exercise_type: Optional[ExerciseTypes] = None
    difficulty_level: Optional[DifficultyLevels] = None
    focus_tenses: Optional[list[Tenses]] = None
    focus_grammar: Optional[list[Grammar]] = None
    focus_topics: Optional[list[Topics]] = None
    start_time: datetime
    end_time: Optional[datetime] = None

class CurrentSession(BaseModel):
    user: User
    current_exercise: Optional[Exercise] = None
    history: list[Exercise] = []



    