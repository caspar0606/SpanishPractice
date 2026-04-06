from datetime import datetime
from typing import Any
from src.domain.classes import Exercise, ExerciseStorage, Progress, ProgressUpdates, Session, SessionStorage, User
from src.core.logging import generate_id


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

from src.app.score import combine_scores

def update_progress(user: User, exercise: ExerciseStorage):

    combine_scores(user.progress, exercise.score)

    return ProgressUpdates(
        id=generate_id(),
        exercise_id=exercise.id,
        time=datetime.now(),
        score=exercise.score,
        new_progress=user.progress
    )

def store_session(session: Session, user: User):
    
    return SessionStorage(
        id=generate_id(),
        start_time=session.start_time,
        end_time=datetime.now(),
        exercises=session.exercise_history,
        progress_updates=session.progress_history
    )