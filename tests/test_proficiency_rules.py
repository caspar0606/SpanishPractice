"""The band must move slowly and only on repeated genuine evidence."""

from src.domain.enums import Band, RelativeLevel
from src.domain.models.profile import Proficiency
from src.domain.rules import proficiency as rules


def run_attempts(start: Band, accuracy: float, count: int):
    """Feeds `count` attempts at a fixed accuracy and reports every band change."""
    prof = Proficiency(current=start)
    changes = []
    for _ in range(count):
        prof = rules.record_attempt(prof, accuracy)
        prof, change = rules.review(prof)
        if change:
            changes.append((change, prof.current))
    return prof, changes


def test_one_perfect_exercise_does_not_promote():
    prof, changes = run_attempts(Band.A2, 1.0, 1)
    assert prof.current is Band.A2
    assert changes == []


def test_a_few_perfect_exercises_still_do_not_promote():
    prof, changes = run_attempts(Band.A2, 1.0, rules.PROMOTION_MIN_ATTEMPTS - 1)
    assert prof.current is Band.A2
    assert changes == []


def test_sustained_excellence_promotes_one_half_step():
    prof, changes = run_attempts(Band.A2, 1.0, rules.PROMOTION_MIN_ATTEMPTS)
    assert changes == [(rules.PROMOTED, Band.A2_5)]
    assert prof.current is Band.A2_5


def test_one_bad_exercise_does_not_demote():
    prof, changes = run_attempts(Band.B1, 0.0, 1)
    assert prof.current is Band.B1
    assert changes == []


def test_sustained_struggle_demotes_one_half_step():
    prof, changes = run_attempts(Band.B1, 0.0, rules.DEMOTION_MIN_ATTEMPTS)
    assert changes == [(rules.DEMOTED, Band.A2_5)]


def test_middling_accuracy_never_moves_the_band():
    prof, changes = run_attempts(Band.A2, 0.7, 60)
    assert prof.current is Band.A2
    assert changes == []


def test_a_promotion_resets_the_evidence():
    """The new band has to be earned again rather than inherited."""
    prof, _ = run_attempts(Band.A2, 1.0, rules.PROMOTION_MIN_ATTEMPTS)
    assert prof.genuine_attempts_at_band == 0
    assert prof.evidence_score == rules.NEUTRAL_EVIDENCE


def test_promotion_is_capped_at_one_step_per_stretch():
    """Even a long perfect run cannot skip bands within one stretch of evidence."""
    prof, changes = run_attempts(Band.A1, 1.0, rules.PROMOTION_MIN_ATTEMPTS * 2 - 1)
    assert len(changes) == 1


def test_band_cannot_run_off_either_end_of_the_scale():
    top, _ = run_attempts(Band.B2, 1.0, rules.PROMOTION_MIN_ATTEMPTS * 3)
    bottom, _ = run_attempts(Band.A1, 0.0, rules.DEMOTION_MIN_ATTEMPTS * 3)
    assert top.current is Band.B2
    assert bottom.current is Band.A1


def test_attempts_until_review_counts_down():
    prof = Proficiency(current=Band.A2)
    assert rules.attempts_until_review(prof) == rules.PROMOTION_MIN_ATTEMPTS
    prof = rules.record_attempt(prof, 0.9)
    assert rules.attempts_until_review(prof) == rules.PROMOTION_MIN_ATTEMPTS - 1


def test_overall_standing_weights_skills_by_how_much_they_were_practised():
    assert rules.overall_standing([]) is None
    assert rules.overall_standing([(0, 1.0)]) is None
    assert rules.overall_standing([(4, 0.5)]) == 0.5
    # 8 attempts at 0.9 outweigh 2 at 0.4.
    assert rules.overall_standing([(8, 0.9), (2, 0.4)]) == 0.8


def test_one_weak_skill_does_not_drag_down_a_strong_learner():
    """The band is overall ability; a lagging skill is recorded on the skill."""
    standing = rules.overall_standing([(5, 0.9), (4, 0.2), (3, 0.6)])
    assert standing > rules.DEMOTION_ACCURACY

    prof = Proficiency(current=Band.A2)
    for _ in range(rules.DEMOTION_MIN_ATTEMPTS * 2):
        prof = rules.record_attempt(prof, standing)
        prof, change = rules.review(prof)
        assert change is None
    assert prof.current is Band.A2


def test_weakness_across_every_skill_still_demotes():
    standing = rules.overall_standing([(5, 0.3), (4, 0.25), (3, 0.35)])
    prof = Proficiency(current=Band.A2)
    changes = []
    for _ in range(rules.DEMOTION_MIN_ATTEMPTS):
        prof = rules.record_attempt(prof, standing)
        prof, change = rules.review(prof)
        if change:
            changes.append(change)
    assert changes == [rules.DEMOTED]


def test_relative_level_needs_a_few_attempts_first():
    assert rules.relative_level(0, 1.0) is RelativeLevel.AT
    assert rules.relative_level(1, 0.0) is RelativeLevel.AT


def test_relative_level_separates_strong_and_weak_skills():
    enough = rules.MIN_ATTEMPTS_FOR_RELATIVE
    assert rules.relative_level(enough, 0.95) is RelativeLevel.ABOVE
    assert rules.relative_level(enough, 0.70) is RelativeLevel.AT
    assert rules.relative_level(enough, 0.30) is RelativeLevel.BELOW
