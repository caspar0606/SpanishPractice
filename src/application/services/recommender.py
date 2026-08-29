"""Builds three next-exercise cards from user state and the curriculum.

Deterministic on purpose: the same learner with the same history must see the
same three cards. The LLM is not consulted.
"""

from src.application import container
from src.domain.enums import (
    ConceptAxis,
    ExerciseStyle,
    ExerciseTypes,
    LengthPreference,
    RecommendationKind,
    Skill,
    WeeklyTime,
)
from src.domain.models.curriculum import ConceptRef, CurriculumStep
from src.domain.models.recommendation import Recommendation
from src.domain.models.user import User
from src.domain.rules import curriculum as curriculum_rules
from src.domain.rules import recommend as rec_rules
from src.domain.rules import vocab as vocab_rules
from src.domain.rules.labels import label_for
from src.domain.rules.score import calculate_score


def recommend(username: str) -> list[Recommendation]:
    user = container.users().load(username)
    if user is None:
        raise ValueError(f"User '{username}' not found")
    if not user.placement.completed:
        raise ValueError("Complete onboarding and the placement test first")

    steps = curriculum_rules.parse_steps(container.content().curriculum())
    return cards_for(user, steps)


def cards_for(user: User, steps: list[CurriculumStep]) -> list[Recommendation]:
    band = user.proficiency.current
    introduced_tenses, introduced_grammar = curriculum_rules.introduced(steps, band)
    nxt = curriculum_rules.next_unlock(steps, band)
    needed = curriculum_rules.weakest_introduced(
        user.progress, introduced_tenses, introduced_grammar,
    )

    blocked = rec_rules.blocked_type(rec_rules.recent_types(user.exercise_history))
    length = user.goals.length_preference if user.goals else LengthPreference.STANDARD
    weekly = user.goals.weekly_time if user.goals else WeeklyTime.T_1_2H
    topic = rec_rules.topic_for_direction(user.goals.direction if user.goals else None)

    cards: list[Recommendation] = []

    due = vocab_rules.due_entries(user.vocab)
    if len(due) >= vocab_rules.REVIEW_BATCH:
        sample = due[: vocab_rules.REVIEW_BATCH]
        cards.append(
            Recommendation(
                kind=RecommendationKind.VOCAB,
                type=ExerciseTypes.DRILLS,
                style=ExerciseStyle.PREFERENCES,
                focus=rec_rules.focus_for_topic(topic),
                estimated_minutes=5,
                title_en=f"Review {len(sample)} words",
                reason_en="A few words from recent exercises are ready to look at again.",
                kind_label=label_for(RecommendationKind.VOCAB),
            ),
        )

    if needed is not None:
        needed_type = rec_rules.pick_type([ExerciseTypes.DRILLS, ExerciseTypes.WRITING], blocked)
        cards.append(_concept_card(RecommendationKind.NEEDED, needed_type, needed, user, length, weekly))

    if nxt is not None:
        roadmap_type = rec_rules.pick_type([ExerciseTypes.DRILLS, ExerciseTypes.READING], blocked)
        cards.append(_concept_card(RecommendationKind.ROADMAP, roadmap_type, nxt, user, length, weekly))
    else:
        fallback_type = rec_rules.pick_type(
            [rec_rules.lagging_skill_type(user, blocked), ExerciseTypes.DRILLS],
            blocked,
        )
        cards.append(
            _topic_card(
                kind=RecommendationKind.ROADMAP,
                exercise_type=fallback_type,
                topic=topic,
                length=length,
                weekly=weekly,
                kind_label="Keep practising",
                reason=(
                    f"You're at the top of the scale. Keep going with "
                    f"{_type_name(fallback_type).lower()} about {label_for(topic).lower()}."
                ),
            ),
        )

    goal_type = rec_rules.pick_type(
        [rec_rules.lagging_skill_type(user, blocked), ExerciseTypes.READING, ExerciseTypes.WRITING],
        blocked,
    )
    topic_name = label_for(topic)
    cards.append(
        _topic_card(
            kind=RecommendationKind.GOAL,
            exercise_type=goal_type,
            topic=topic,
            length=length,
            weekly=weekly,
            kind_label=label_for(RecommendationKind.GOAL),
            reason=(
                f"You're learning Spanish for {topic_name.lower()}, "
                f"so this {_type_name(goal_type).lower()} is about that."
            ),
        ),
    )
    return cards[:3]


def _type_name(exercise_type: ExerciseTypes) -> str:
    try:
        return label_for(Skill(exercise_type.value))
    except ValueError:
        return exercise_type.value.replace("_", " ").capitalize()


def _concept_card(
    kind: RecommendationKind,
    exercise_type: ExerciseTypes,
    concept: ConceptRef,
    user: User,
    length: LengthPreference,
    weekly: WeeklyTime,
) -> Recommendation:
    member = concept.member()
    name = label_for(member)
    bucket = user.progress.tenses if concept.axis is ConceptAxis.TENSE else user.progress.grammar
    if kind is RecommendationKind.NEEDED:
        stats = bucket.get(member)
        practised = stats is not None and stats.total_attempts > 0
        if practised and stats is not None:
            score = round(calculate_score(stats))
            reason = f"{name} is your weakest practised area so far ({score}%)."
        else:
            reason = f"You haven't practised {name.lower()} yet, so we'll start there."
        title = f"{name} drills" if exercise_type is ExerciseTypes.DRILLS else f"Writing: {name}"
    else:
        reason = f"{name} is the next concept on the roadmap. We'll keep it at your current level."
        if exercise_type is ExerciseTypes.READING:
            title = f"Reading: {name}"
        elif exercise_type is ExerciseTypes.WRITING:
            title = f"Writing: {name}"
        else:
            title = f"{name} drills"

    return Recommendation(
        kind=kind,
        type=exercise_type,
        style=ExerciseStyle.PREFERENCES,
        focus=rec_rules.focus_for_concept(concept),
        estimated_minutes=rec_rules.estimated_minutes(exercise_type, length, weekly),
        title_en=title,
        reason_en=reason,
        kind_label=label_for(kind),
    )


def _topic_card(
    kind: RecommendationKind,
    exercise_type: ExerciseTypes,
    topic,
    length: LengthPreference,
    weekly: WeeklyTime,
    kind_label: str,
    reason: str,
) -> Recommendation:
    title = f"{_type_name(exercise_type)} on {label_for(topic).lower()}"
    return Recommendation(
        kind=kind,
        type=exercise_type,
        style=ExerciseStyle.PREFERENCES,
        focus=rec_rules.focus_for_topic(topic),
        estimated_minutes=rec_rules.estimated_minutes(exercise_type, length, weekly),
        title_en=title,
        reason_en=reason,
        kind_label=kind_label,
    )
