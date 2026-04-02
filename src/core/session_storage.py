from datetime import datetime
from pydantic import BaseModel
from typing import Any, Optional

from domain.classes import AreasOfFocus, Exercise, ExerciseTypes, Progress

class ExerciseStorage(BaseModel):
    id: str
    start_time: datetime
    end_time: datetime
    type: ExerciseTypes
    areas_of_focus: AreasOfFocus
    prompt: Any
    user_response: Any
    feedback: Any
    exercise_score: Progress

class ProgressUpdates(BaseModel):
    id: str
    exercise_id: str
    time: datetime
    exercise_score: Progress
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
        exercise_score=progress
    )