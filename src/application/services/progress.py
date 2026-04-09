from datetime import datetime
from typing import Any

from src.domain.models.exercise import ExerciseStorage
from src.domain.models.progress import Progress, ProgressUpdates
from src.domain.models.user import User
from src.domain.rules.score import add_scores, combine_scores
from src.domain.utils import initialise_progress
from src.infrastructure.config.logging import generate_id
from src.infrastructure.persistence.file_storage import load_user_state, save_user_state

def return_progress(username: str):
    user = load_user_state(username)

    if user is None:
        raise ValueError()
    
    return user.progress

def save_user_progress(user: User, response: Any, feedback: Any, score: Any):

    if user.current_exercise is None or user.current_exercise.prompt is None:
        raise ValueError(f"User current storage not found")

    user.current_exercise.user_response = response
    user.current_exercise.feedback = feedback
    user.current_exercise.score = score
    user.current_exercise.end_time = datetime.now()
    
    finished_exercise = user.current_exercise

    user.exercise_history.append(finished_exercise)
    user.progress_history.append(update_progress(user, finished_exercise))

    save_user_state(user)


def build_drill_progress_update(exercise_context, feedback) -> Progress:
    prog = initialise_progress()
    stats = feedback.stats
    aofs = exercise_context.areas_of_focus

    if aofs.focus_tenses:
        for tense in aofs.focus_tenses:
            if tense is not None:
                add_scores(prog.tenses[tense], stats)

    if aofs.focus_topics:
        for topic in aofs.focus_topics:
            if topic is not None:
                add_scores(prog.topics[topic], stats)

    if aofs.focus_grammar:
        for grammar in aofs.focus_grammar:
            if grammar is not None:
                add_scores(prog.grammar[grammar], stats)

    return prog

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