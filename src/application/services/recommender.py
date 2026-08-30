"""Builds today's four practice slots from user state and the curriculum.

Deterministic on purpose: the same learner with the same history on the same
day must see the same plan. The LLM is not consulted.
"""

from datetime import date

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
from src.domain.models.exercise import AreasOfFocus
from src.domain.models.recommendation import DailySlot, HomePlan, Recommendation
from src.domain.models.user import User
from src.domain.rules import curriculum as curriculum_rules
from src.domain.rules import recommend as rec_rules
from src.domain.rules import vocab as vocab_rules
from src.domain.rules.labels import label_for
from src.domain.rules.score import calculate_score


def recommend(
    username: str,
    today: date | None = None,
    tz_offset_minutes: int | None = None,
) -> HomePlan:
    user = container.users().load(username)
    if user is None:
        raise ValueError(f"User '{username}' not found")
    if not user.placement.completed:
        raise ValueError("Complete onboarding and the placement test first")

    steps = curriculum_rules.parse_steps(container.content().curriculum())
    return plan_for(user, steps, today, tz_offset_minutes)


def plan_for(
    user: User,
    steps: list[CurriculumStep],
    today: date | None = None,
    tz_offset_minutes: int | None = None,
) -> HomePlan:
    today = today or date.today()
    band = user.proficiency.current
    introduced_tenses, introduced_grammar = curriculum_rules.introduced(steps, band)
    nxt = curriculum_rules.next_unlock(steps, band)
    needed = curriculum_rules.weakest_introduced(
        user.progress, introduced_tenses, introduced_grammar,
    )
    length = user.goals.length_preference if user.goals else LengthPreference.STANDARD
    weekly = user.goals.weekly_time if user.goals else WeeklyTime.T_1_2H
    topic = rec_rules.topic_for_direction(user.goals.direction if user.goals else None)
    done_types = rec_rules.completed_daily_types(user.exercise_history, today, tz_offset_minutes)

    daily: list[DailySlot] = []
    for skill_type in rec_rules.DAILY_TYPES:
        focus, reason = _daily_focus_and_reason(skill_type, needed, nxt, topic)
        title = _skill_name(skill_type)
        minutes = rec_rules.estimated_minutes(skill_type, length, weekly)
        done = skill_type in done_types
        daily.append(
            DailySlot(
                type=skill_type,
                done=done,
                title_en=title,
                reason_en="Done for today." if done else reason,
                kind_label="Done" if done else label_for(RecommendationKind.DAILY),
                estimated_minutes=0 if done else minutes,
                style=ExerciseStyle.PREFERENCES,
                focus=focus,
            ),
        )

    extras: list[Recommendation] = []
    due = vocab_rules.due_entries(user.vocab)
    if len(due) >= vocab_rules.REVIEW_BATCH:
        sample = due[: vocab_rules.REVIEW_BATCH]
        extras.append(
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

    remaining = sum(1 for slot in daily if not slot.done)
    if remaining == 0 and needed is not None:
        extras.append(
            _concept_card(
                RecommendationKind.EXTRA,
                ExerciseTypes.DRILLS,
                needed,
                user,
                length,
                weekly,
            ),
        )

    return HomePlan(
        remaining=remaining,
        complete=remaining == 0,
        daily=daily,
        extras=extras,
    )


def startable_cards(plan: HomePlan) -> list[Recommendation]:
    """Daily slots that still need doing, in the shape generate already accepts."""
    return [
        Recommendation(
            kind=RecommendationKind.DAILY,
            type=slot.type,
            style=slot.style,
            focus=slot.focus,
            estimated_minutes=slot.estimated_minutes,
            title_en=slot.title_en,
            reason_en=slot.reason_en,
            kind_label=slot.kind_label,
        )
        for slot in plan.daily
        if not slot.done
    ]


def _skill_name(exercise_type: ExerciseTypes) -> str:
    try:
        return label_for(Skill(exercise_type.value))
    except ValueError:
        return exercise_type.value.replace("_", " ").capitalize()


def _daily_focus_and_reason(
    skill_type: ExerciseTypes,
    needed: ConceptRef | None,
    nxt: ConceptRef | None,
    topic,
) -> tuple[AreasOfFocus, str]:
    topic_name = label_for(topic).lower()
    if skill_type is ExerciseTypes.WRITING:
        if needed is not None:
            name = label_for(needed.member()).lower()
            return rec_rules.focus_for_concept(needed), f"A short piece using {name}."
        return rec_rules.focus_for_topic(topic), f"A short piece about {topic_name}."
    if skill_type is ExerciseTypes.READING:
        if nxt is not None:
            name = label_for(nxt.member()).lower()
            return rec_rules.focus_for_concept(nxt), f"A passage that uses {name}."
        return rec_rules.focus_for_topic(topic), f"A passage about {topic_name}."
    if skill_type is ExerciseTypes.LISTENING:
        return rec_rules.focus_for_topic(topic), f"Listen for {topic_name} language."
    if needed is not None:
        name = label_for(needed.member()).lower()
        return rec_rules.focus_for_concept(needed), f"Say a few sentences using {name}."
    return rec_rules.focus_for_topic(topic), f"Speak about {topic_name}."


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
    stats = bucket.get(member)
    practised = stats is not None and stats.total_attempts > 0
    if practised and stats is not None:
        score = round(calculate_score(stats))
        reason = f"{name} is your weakest practised area so far ({score}%)."
    else:
        reason = f"You haven't practised {name.lower()} yet, so we'll start there."
    title = f"{name} drills" if exercise_type is ExerciseTypes.DRILLS else f"{_skill_name(exercise_type)}: {name}"
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
