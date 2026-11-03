from datetime import datetime
from typing import Any

from src.domain.models.progress import Progress
from src.domain.models.exercise import Exercise, ExerciseConfig
from src.domain.models.session import ExerciseStorage, Session, SessionStorage, User
from src.domain.rules.band import cefr_hint, word_count_for
from src.infrastructure.config.logging import generate_id


def store_exercise(exercise: Exercise, progress: Progress, prompt: Any, user_response: Any, feedback: Any):

    return ExerciseStorage(
        id=exercise.id,
        start_time=exercise.start_time,
        end_time=datetime.now(),
        exercise_config=ExerciseConfig(
            band=exercise.band,
            length=exercise.length,
            word_count=word_count_for(exercise.exercise_type, exercise.band, exercise.length),
            cefr_hint=cefr_hint(exercise.band)),
        type=exercise.exercise_type,
        areas_of_focus=exercise.areas_of_focus,
        prompt=prompt,
        user_response=user_response,
        feedback=feedback,
        score=progress
    )


def store_session(session: Session, user: User):
    
    return SessionStorage(
        id=generate_id(),
        start_time=session.start_time,
        end_time=datetime.now(),
        exercises=session.exercise_history,
        progress_updates=session.progress_history
    )
