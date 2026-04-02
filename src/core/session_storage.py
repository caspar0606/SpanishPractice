from datetime import datetime
from pydantic import BaseModel
from typing import Any, Optional

from src.domain.classes import AreasOfFocus, Exercise, ExerciseTypes, Progress
from src.core.logging import generate_id

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


def store_exercise(exercise: Exercise, progress: Progress, prompt: Any, user_response: Any, feedback: Any):

    return ExerciseStorage(
        id=exercise.id,
        start_time=exercise.start_time,
        end_time=datetime.now(),
        type=exercise.exercise_type,
        areas_of_focus=exercise.areas_of_focus,
        prompt=prompt,
        user_response=user_response,
        feedback=feedback,
        score=progress
    )

def update_progress(exercise: ExerciseStorage, progress: Progress):

    return ProgressUpdates(
        id=generate_id(),
        exercise_id=exercise.id,
        time=datetime.now(),
        score=exercise.score,
        new_progress=None
    )