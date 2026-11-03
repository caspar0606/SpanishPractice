from datetime import datetime

from src.application import container
from src.domain.enums import Band, OnboardingStep
from src.domain.models.profile import Proficiency, UserGoals
from src.domain.models.user import User
from src.domain.rules import band as band_rules


def _load(username: str) -> User:
    user = container.users().load(username)
    if user is None:
        raise ValueError(f"User '{username}' not found")
    return user


def current_step(user: User) -> OnboardingStep:
    if user.goals is None:
        return OnboardingStep.GOALS
    if not user.placement.completed:
        return OnboardingStep.PLACEMENT
    return OnboardingStep.READY


def step_for(username: str) -> OnboardingStep:
    return current_step(_load(username))


def save_goals(username: str, goals: UserGoals) -> User:
    user = _load(username)
    user.goals = goals

    # Until placement runs, assume the floor rather than the learner's ambition.
    if not user.placement.completed:
        user.proficiency = Proficiency(current=Band.A1, updated_at=datetime.now())

    container.users().save(user)
    return user


def plan_summary(user: User) -> dict:
    """Plain-English framing of where the learner is and what is next."""
    band = user.proficiency.current

    if user.goals is None:
        return {
            "current_band": band.value,
            "current_level": band_rules.display_level(band),
            "current_gloss": band_rules.gloss(band),
            "target_band": None,
            "target_level": None,
            "target_gloss": None,
            "half_steps_remaining": None,
            "estimated_weeks": None,
            "completed_exercises": len(user.exercise_history),
        }

    target = user.goals.desired_band
    remaining = max(0, band_rules.rank(target) - band_rules.rank(band))

    weeks = 0
    cursor = band
    for _ in range(remaining):
        weeks += band_rules.hours_to_next_band(cursor, user.goals.weekly_time)
        cursor = band_rules.shift(cursor, 1)

    return {
        "current_band": band.value,
        "current_level": band_rules.display_level(band),
        "current_gloss": band_rules.gloss(band),
        "target_band": target.value,
        "target_level": band_rules.display_level(target),
        "target_gloss": band_rules.gloss(target),
        "half_steps_remaining": remaining,
        "estimated_weeks": weeks or None,
        "completed_exercises": len(user.exercise_history),
    }
