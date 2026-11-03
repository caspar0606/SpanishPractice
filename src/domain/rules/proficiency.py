"""Moves the learner's band, deliberately slowly.

The band is the app's claim about what someone can do, so it should only change
on repeated genuine evidence. A single good or bad exercise never moves it.
"""

from datetime import datetime
from typing import Iterable

from src.domain.enums import RelativeLevel
from src.domain.models.profile import Proficiency
from src.domain.rules.band import rank, shift

PROMOTION_MIN_ATTEMPTS = 12
PROMOTION_ACCURACY = 0.85
DEMOTION_MIN_ATTEMPTS = 8
DEMOTION_ACCURACY = 0.45

# Where evidence restarts after a band change, so the new band must be re-earned.
NEUTRAL_EVIDENCE = 0.65

# Weight of the newest attempt in the rolling average.
EWMA_ALPHA = 0.25

ABOVE_ACCURACY = 0.85
BELOW_ACCURACY = 0.50
MIN_ATTEMPTS_FOR_RELATIVE = 3

PROMOTED = "promoted"
DEMOTED = "demoted"


def blend(previous: float, attempts: int, accuracy: float) -> float:
    """Exponential moving average, seeded by the first attempt.

    Used within a single skill, where recent work is the better signal.
    """
    if attempts <= 0:
        return accuracy
    return previous + EWMA_ALPHA * (accuracy - previous)


def overall_standing(skills: Iterable[tuple[int, float]]) -> float | None:
    """The learner's ability across all skills, as attempt-weighted accuracy.

    Averaging across skills rather than over the raw stream of exercises keeps
    the band from tracking whatever was practised most recently, so a run of
    reading cannot pull down someone whose writing is strong. Lagging skills are
    recorded as a relative level on the skill itself instead.
    """
    weight = 0
    total = 0.0
    for attempts, accuracy in skills:
        if attempts <= 0:
            continue
        weight += attempts
        total += attempts * accuracy

    if weight == 0:
        return None

    return total / weight


def record_attempt(proficiency: Proficiency, standing: float) -> Proficiency:
    """Bank one more piece of genuine evidence for the current band."""
    return proficiency.model_copy(
        update={
            "evidence_score": standing,
            "genuine_attempts_at_band": proficiency.genuine_attempts_at_band + 1,
        },
    )


def review(proficiency: Proficiency) -> tuple[Proficiency, str | None]:
    """Promote or demote if the evidence at this band is strong enough.

    Returns the proficiency plus a note naming the change, or None if the band
    held. A change resets the evidence so the new band has to be earned again.
    """
    attempts = proficiency.genuine_attempts_at_band
    evidence = proficiency.evidence_score
    current = proficiency.current

    if attempts >= PROMOTION_MIN_ATTEMPTS and evidence >= PROMOTION_ACCURACY:
        target = shift(current, 1)
        change = PROMOTED
    elif attempts >= DEMOTION_MIN_ATTEMPTS and evidence <= DEMOTION_ACCURACY:
        target = shift(current, -1)
        change = DEMOTED
    else:
        return proficiency, None

    if rank(target) == rank(current):
        # Already at the top or bottom of the scale.
        return proficiency, None

    moved = proficiency.model_copy(
        update={
            "current": target,
            "updated_at": datetime.now(),
            "genuine_attempts_at_band": 0,
            "evidence_score": NEUTRAL_EVIDENCE,
        },
    )
    return moved, change


def attempts_until_review(proficiency: Proficiency) -> int:
    """How many more genuine attempts before a promotion could be considered."""
    return max(0, PROMOTION_MIN_ATTEMPTS - proficiency.genuine_attempts_at_band)


def relative_level(genuine_attempts: int, accuracy: float) -> RelativeLevel:
    """Where a single skill sits against the learner's overall band."""
    if genuine_attempts < MIN_ATTEMPTS_FOR_RELATIVE:
        return RelativeLevel.AT
    if accuracy >= ABOVE_ACCURACY:
        return RelativeLevel.ABOVE
    if accuracy <= BELOW_ACCURACY:
        return RelativeLevel.BELOW
    return RelativeLevel.AT
