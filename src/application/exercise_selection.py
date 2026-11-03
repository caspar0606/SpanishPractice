from datetime import datetime
from typing import Any

from src.application import container
from src.domain.enums import (
    Band,
    ExerciseStyle,
    ExerciseTypes,
    Grammar,
    LengthPreference,
    Tenses,
    Topics,
    is_category_sentinel,
)
from src.domain.models.exercise import (
    AreasOfFocus,
    Exercise,
    ExerciseConfig,
    ExerciseContext,
    ExerciseStorage,
)
from src.domain.models.user import User
from src.domain.rules import band as band_rules
from src.domain.rules.config import FOCUS_CONFIG
from src.domain.rules.score import calculate_score
from src.infrastructure.config.logging import generate_id

UNFINISHED_EXERCISE = "You have an unfinished exercise"


def _weakest_keys(progress_map: dict, count: int, allowed: list | None = None) -> list:
    """Weakest tracked keys, restricted to what the band has introduced."""
    permitted = set(allowed) if allowed else None
    candidates = (
        (key, stats)
        for key, stats in progress_map.items()
        if not is_category_sentinel(key) and (permitted is None or key in permitted)
    )
    ranked = sorted(candidates, key=lambda item: calculate_score(item[1]))
    return [key for key, _ in ranked[:count]]


def user_band(user: User) -> Band:
    return user.proficiency.current


def user_length(user: User) -> LengthPreference:
    return user.goals.length_preference if user.goals else LengthPreference.STANDARD


def build_exercise_config(
    exercise_type: ExerciseTypes,
    band: Band,
    length: LengthPreference,
) -> ExerciseConfig:
    return ExerciseConfig(
        band=band,
        level=band_rules.display_level(band),
        length=length,
        word_count=band_rules.word_count_for(exercise_type, band, length),
        question_count=0,
        cefr_hint=band_rules.cefr_hint(band),
    )


def generate_exercise(
    username: str,
    type: ExerciseTypes,
    style: ExerciseStyle,
    preferences: AreasOfFocus | None,
    length: LengthPreference | None = None,
    replace: bool = False,
) -> Exercise:
    user = container.users().load(username)

    if user is None:
        raise ValueError(f"User '{username}' not found")

    if not user.placement.completed:
        raise ValueError("Complete onboarding and the placement test first")

    if _in_progress(user) and not replace:
        raise ValueError(
            f"{UNFINISHED_EXERCISE}. Finish it first, or confirm you want to replace it.",
        )

    band = user_band(user)
    length = length or user_length(user)

    if style is ExerciseStyle.PREFERENCES:
        if preferences is None:
            raise ValueError("Preferences is incorrectly NULL")
        areas_of_focus = preferences

    else:
        areas_of_focus = weak_areas(band, preferences, type, user)

    exercise = Exercise(
        id=generate_id(),
        exercise_type=type,
        band=band,
        length=length,
        areas_of_focus=areas_of_focus,
        start_time=datetime.now(),
    )

    user.current_exercise = ExerciseStorage(
        id=exercise.id,
        type=type,
        areas_of_focus=areas_of_focus,
        exercise_config=build_exercise_config(type, band, length),
        start_time=datetime.now(),
    )

    container.users().save(user)
    return exercise


def _in_progress(user: User) -> bool:
    current = user.current_exercise
    return (
        current is not None
        and current.prompt is not None
        and current.end_time is None
        and current.user_response is None
    )


def weak_areas(
    band: Band,
    preferences: AreasOfFocus | None,
    type: ExerciseTypes,
    user: User,
) -> AreasOfFocus:
    num_tenses, num_grammar, num_topics = band_rules.focus_counts(band)
    counts = {"num_tenses": num_tenses, "num_grammar": num_grammar, "num_topics": num_topics}
    allowed_tenses = band_rules.allowed_tenses(band)
    allowed_grammar = band_rules.allowed_grammar(band)

    if (type is ExerciseTypes.DRILLS) and (
        (preferences is None)
        or (
            preferences.focus_tenses is None
            and preferences.focus_grammar is None
            and preferences.focus_topics is None
        )
    ):
        raise ValueError("Preferences is incorrectly NULL or incomplete for drills")

    if type is ExerciseTypes.DRILLS:
        focus, loc, num = next(
            FOCUS_CONFIG[topic]
            for topic in FOCUS_CONFIG
            if getattr(preferences, topic) is not None
        )

        allowed = {"tenses": allowed_tenses, "grammar": allowed_grammar}.get(focus.value)
        focus_list = _weakest_keys(
            getattr(user.progress, focus.value),
            counts[num],
            allowed,
        )

        map_list: list[list[Any] | None] = [None, None, None]
        map_list[loc] = focus_list

        return AreasOfFocus(
            focus_tenses=map_list[0],
            focus_grammar=map_list[1],
            focus_topics=map_list[2],
        )

    return AreasOfFocus(
        focus_tenses=[
            Tenses(tense)
            for tense in _weakest_keys(user.progress.tenses, num_tenses, allowed_tenses)
        ],
        focus_grammar=[
            Grammar(grammar)
            for grammar in _weakest_keys(user.progress.grammar, num_grammar, allowed_grammar)
        ],
        focus_topics=[
            Topics(topic) for topic in _weakest_keys(user.progress.topics, num_topics)
        ],
    )


def create_exercise_context(exercise: Exercise) -> ExerciseContext:
    return ExerciseContext(
        areas_of_focus=exercise.areas_of_focus,
        exercise_config=build_exercise_config(
            exercise.exercise_type,
            exercise.band,
            exercise.length,
        ),
    )
