"""Pure helpers the recommender uses to pick type, topic, and duration.

Kept in the domain so the application service is only orchestration.
"""

from datetime import date

from src.domain.enums import (
    ConceptAxis,
    Direction,
    ExerciseTypes,
    LengthPreference,
    Topics,
    WeeklyTime,
)
from src.domain.models.curriculum import ConceptRef
from src.domain.models.exercise import AreasOfFocus, ExerciseStorage
from src.domain.models.user import User

# Listening and speaking are generated once Phase 7 is wired.
AVAILABLE_TYPES: tuple[ExerciseTypes, ...] = (
    ExerciseTypes.WRITING,
    ExerciseTypes.READING,
    ExerciseTypes.DRILLS,
    ExerciseTypes.LISTENING,
    ExerciseTypes.SPEAKING,
)

DIRECTION_TOPIC: dict[Direction, Topics] = {
    Direction.TRAVEL: Topics.TRAVEL,
    Direction.SCHOOL: Topics.SCHOOL,
    Direction.WORK: Topics.WORK,
    Direction.SOCIAL: Topics.RELATIONSHIPS,
    Direction.PERSONAL: Topics.EMOTIONS,
}

_MINUTES: dict[ExerciseTypes, dict[LengthPreference, int]] = {
    ExerciseTypes.WRITING: {
        LengthPreference.SHORT: 10,
        LengthPreference.STANDARD: 15,
        LengthPreference.LONG: 25,
    },
    ExerciseTypes.READING: {
        LengthPreference.SHORT: 8,
        LengthPreference.STANDARD: 12,
        LengthPreference.LONG: 18,
    },
    ExerciseTypes.DRILLS: {
        LengthPreference.SHORT: 8,
        LengthPreference.STANDARD: 10,
        LengthPreference.LONG: 12,
    },
    ExerciseTypes.LISTENING: {
        LengthPreference.SHORT: 6,
        LengthPreference.STANDARD: 8,
        LengthPreference.LONG: 12,
    },
    ExerciseTypes.SPEAKING: {
        LengthPreference.SHORT: 6,
        LengthPreference.STANDARD: 8,
        LengthPreference.LONG: 12,
    },
}

STREAK_TO_AVOID = 3

DAILY_TYPES: tuple[ExerciseTypes, ...] = (
    ExerciseTypes.WRITING,
    ExerciseTypes.READING,
    ExerciseTypes.LISTENING,
    ExerciseTypes.SPEAKING,
)


def topic_for_direction(direction: Direction | None) -> Topics:
    if direction is None:
        return Topics.TRAVEL
    return DIRECTION_TOPIC.get(direction, Topics.TRAVEL)


def estimated_minutes(
    exercise_type: ExerciseTypes,
    length: LengthPreference,
    weekly: WeeklyTime | None = None,
) -> int:
    table = _MINUTES.get(exercise_type, _MINUTES[ExerciseTypes.DRILLS])
    minutes = table.get(length, 10)
    if weekly in {WeeklyTime.T_30_60M, WeeklyTime.T_1_2H}:
        return min(minutes, 12)
    return minutes


def recent_types(history: list[ExerciseStorage], limit: int = STREAK_TO_AVOID) -> list[ExerciseTypes]:
    """Most recent genuine exercise types, newest first."""
    found: list[ExerciseTypes] = []
    for exercise in reversed(history):
        if exercise.genuine is False:
            continue
        found.append(exercise.type)
        if len(found) >= limit:
            break
    return found


def blocked_type(recent: list[ExerciseTypes]) -> ExerciseTypes | None:
    """The type we must not pick next, if the last three were all the same."""
    if len(recent) >= STREAK_TO_AVOID and len(set(recent[:STREAK_TO_AVOID])) == 1:
        return recent[0]
    return None


def pick_type(
    preferred: list[ExerciseTypes],
    blocked: ExerciseTypes | None,
    already: set[ExerciseTypes] | None = None,
) -> ExerciseTypes:
    """First preferred type that is available, generated, and not overused."""
    taken = already or set()
    for candidate in preferred:
        if candidate is blocked or candidate in taken or candidate not in AVAILABLE_TYPES:
            continue
        return candidate
    for candidate in AVAILABLE_TYPES:
        if candidate is not blocked and candidate not in taken:
            return candidate
    for candidate in AVAILABLE_TYPES:
        if candidate not in taken:
            return candidate
    return ExerciseTypes.DRILLS


def genuine_counts(user: User) -> dict[ExerciseTypes, int]:
    counts = {kind: 0 for kind in AVAILABLE_TYPES}
    for skill, entry in user.skills.items():
        try:
            kind = ExerciseTypes(skill.value)
        except ValueError:
            continue
        if kind in counts:
            counts[kind] = entry.genuine_attempts
    return counts


def lagging_skill_type(user: User, blocked: ExerciseTypes | None) -> ExerciseTypes:
    """The under-practised productive skill, used for the goal-aligned card."""
    counts = genuine_counts(user)
    ranked = sorted(
        (
            ExerciseTypes.WRITING,
            ExerciseTypes.READING,
            ExerciseTypes.LISTENING,
            ExerciseTypes.SPEAKING,
        ),
        key=lambda kind: (counts.get(kind, 0), 0 if kind is ExerciseTypes.WRITING else 1),
    )
    return pick_type(list(ranked), blocked)


def focus_for_concept(concept: ConceptRef) -> AreasOfFocus:
    if concept.axis is ConceptAxis.TENSE:
        return AreasOfFocus(focus_tenses=[concept.member()])  # type: ignore[list-item]
    return AreasOfFocus(focus_grammar=[concept.member()])  # type: ignore[list-item]


def focus_for_topic(topic: Topics) -> AreasOfFocus:
    return AreasOfFocus(focus_topics=[topic])


def completed_daily_types(history: list[ExerciseStorage], day: date) -> set[ExerciseTypes]:
    """Skills already submitted on this calendar day."""
    done: set[ExerciseTypes] = set()
    for exercise in history:
        when = exercise.end_time
        if when is None or exercise.type not in DAILY_TYPES:
            continue
        if when.date() == day:
            done.add(exercise.type)
    return done
