from datetime import datetime
from typing import Any

from src.domain.enums import (
    DifficultyLevels,
    ExerciseStyle,
    ExerciseTypes,
    Grammar,
    Tenses,
    Topics,
    is_category_sentinel,
)
from src.domain.models.exercise import AreasOfFocus, Exercise, ExerciseConfig
from src.domain.models.session import ExerciseStorage, User
from src.domain.rules.config import DIFFICULTY_CONFIG, FOCUS_CONFIG, word_count_for
from src.domain.rules.score import calculate_score
from src.infrastructure.config.logging import generate_id
from src.infrastructure.llm.contracts.shared import ExerciseContext
from src.infrastructure.persistence.file_storage import load_user_state, save_user_state


def _weakest_keys(progress_map: dict, count: int) -> list:
    ranked = sorted(
        ((key, stats) for key, stats in progress_map.items() if not is_category_sentinel(key)),
        key=lambda item: calculate_score(item[1]),
    )
    return [key for key, _ in ranked[:count]]


def generate_exercise(username: str, type: ExerciseTypes, difficulty: 
                      DifficultyLevels, style: ExerciseStyle, preferences: AreasOfFocus | None) -> Exercise:
    
    user = load_user_state(username)

    if user is None:
        raise ValueError(f"User '{username}' not found")
    
    if (style is ExerciseStyle.PREFERENCES):
        if preferences is None:
            raise ValueError("Preferences is incorrectly NULL")
        areas_of_focus = preferences

    else:
        areas_of_focus = weak_areas(difficulty, preferences, type, user)
        
    exercise = Exercise(
        id=generate_id(),
        exercise_type=type,
        difficulty_level=difficulty,
        areas_of_focus=areas_of_focus,
        start_time=datetime.now(),
        )
    
    user.current_exercise = ExerciseStorage(
        id=exercise.id,
        type=type,
        areas_of_focus=areas_of_focus,
        exercise_config=ExerciseConfig(
            difficulty=difficulty,
            word_count=word_count_for(type, difficulty)),
        start_time=datetime.now())

    save_user_state(user)
    return exercise


def weak_areas(difficulty_level: DifficultyLevels, preferences: AreasOfFocus | None, type: ExerciseTypes, user: User) -> AreasOfFocus:
    config = DIFFICULTY_CONFIG[difficulty_level] 

    if ((type is ExerciseTypes.DRILLS) and ((preferences is None) or (preferences.focus_tenses is None and \
                                                                        preferences.focus_grammar is None and \
                                                                        preferences.focus_topics is None))):
        raise ValueError("Preferences is incorrectly NULL or incomplete for drills")

    if type is ExerciseTypes.DRILLS:
        focus, loc, num = next(
            FOCUS_CONFIG[topic]
            for topic in FOCUS_CONFIG
            if getattr(preferences, topic) is not None
        )

        focus_list = _weakest_keys(getattr(user.progress, focus.value), getattr(config, num))

        map_list: list[list[Any] | None] = [None, None, None]
        map_list[loc] = focus_list
        
        return AreasOfFocus(focus_tenses=map_list[0], focus_grammar=map_list[1], focus_topics=map_list[2])

    return AreasOfFocus(
        focus_tenses=[Tenses(tense) for tense in _weakest_keys(user.progress.tenses, config.num_tenses)],
        focus_grammar=[Grammar(grammar) for grammar in _weakest_keys(user.progress.grammar, config.num_grammar)],
        focus_topics=[Topics(topic) for topic in _weakest_keys(user.progress.topics, config.num_topics)],
    )


def create_exercise_context(exercise: Exercise) -> ExerciseContext:
    return ExerciseContext(
        areas_of_focus=exercise.areas_of_focus,
        exercise_config=ExerciseConfig(
            difficulty=exercise.difficulty_level,
            word_count=word_count_for(exercise.exercise_type, exercise.difficulty_level))
    )
