from datetime import datetime
from typing import Any
from src.domain.enums import ExerciseTypes
from src.domain.models.progress import Progress, ProgressUpdates
from src.domain.models.exercise import Exercise, ExerciseConfig
from src.domain.models.session import ExerciseStorage, Session, SessionStorage, User
from src.domain.rules.config import DIFFICULTY_CONFIG
from src.infrastructure.config.logging import generate_id


def store_exercise(exercise: Exercise, progress: Progress, prompt: Any, user_response: Any, feedback: Any):

    return ExerciseStorage(
        id=exercise.id,
        start_time=exercise.start_time,
        end_time=datetime.now(),
        exercise_config=ExerciseConfig(
            difficulty=exercise.difficulty_level,
            word_count=(DIFFICULTY_CONFIG[exercise.difficulty_level].r_word_count if exercise.exercise_type is \
            ExerciseTypes.READING else DIFFICULTY_CONFIG[exercise.difficulty_level].w_word_count)),
        type=exercise.exercise_type,
        areas_of_focus=exercise.areas_of_focus,
        prompt=prompt,
        user_response=user_response,
        feedback=feedback,
        score=progress
    )

from src.domain.rules.score import combine_scores

def update_progress(user: User, exercise: ExerciseStorage):
    if exercise.score is None:
        raise ValueError(f"Exercise {exercise.id} is invalid")
    
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