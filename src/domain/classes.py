from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field
from src.domain.enums import Tenses, Grammar, Topics, DifficultyLevels, ExerciseTypes


class ComputeStats(BaseModel):
    total_attempts: float = 0
    correct_attempts: float = 0

class Progress(BaseModel):
    tenses: dict[Tenses, ComputeStats]
    grammar: dict[Grammar, ComputeStats] 
    topics: dict[Topics, ComputeStats]

class AreasOfFocus(BaseModel):
    focus_tenses: Optional[list[Tenses]] = None
    focus_grammar: Optional[list[Grammar]] = None
    focus_topics: Optional[list[Topics]] = None

class Exercise(BaseModel):
    id: str
    exercise_type: ExerciseTypes
    difficulty_level: DifficultyLevels
    areas_of_focus: AreasOfFocus
    start_time: datetime
    end_time: Optional[datetime] = None


class ExerciseStorage(BaseModel):
    id: str
    start_time: datetime
    end_time: datetime
    type: ExerciseTypes
    areas_of_focus: AreasOfFocus
    prompt: Any
    user_response: Any
    feedback: Any
    score: Progress

class ProgressUpdates(BaseModel):
    id: str
    exercise_id: str
    time: datetime
    score: Progress
    new_progress: Progress

class SessionStorage(BaseModel):
    id: str
    start_time: datetime
    end_time: datetime
    exercises: Optional[list[ExerciseStorage]]
    progress_updates: Optional[list[ProgressUpdates]]


class User(BaseModel):
    name: str
    progress: Progress
    first_time: bool
    history: list[SessionStorage] = Field(default_factory=list)
    progress_history: list[ProgressUpdates] = Field(default_factory=list)

class Session(BaseModel):
    id: str
    user: User
    start_time: datetime
    current_exercise: Exercise
    exercise_history: list[ExerciseStorage]
    progress_history: list[ProgressUpdates]



    