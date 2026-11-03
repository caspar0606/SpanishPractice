from src.domain.models.exercise import AttemptMetrics
from src.domain.rules import genuine


def prose(seconds=120.0, words=60, target=100):
    return AttemptMetrics(seconds_spent=seconds, response_words=words, target_words=target)


def drills(seconds=120.0, answered=10, total=10):
    return AttemptMetrics(seconds_spent=seconds, items_answered=answered, items_total=total)


def test_a_real_written_attempt_counts():
    verdict = genuine.judge(prose())
    assert verdict.genuine is True
    assert verdict.reasons == []


def test_blank_response_is_not_genuine():
    verdict = genuine.judge(prose(words=0))
    assert verdict.genuine is False
    assert verdict.reasons


def test_one_word_response_is_not_genuine():
    assert genuine.judge(prose(words=1)).genuine is False


def test_instant_submission_is_not_genuine():
    """Enough words but submitted in two seconds, so it was pasted or prefilled."""
    verdict = genuine.judge(prose(seconds=2.0, words=90))
    assert verdict.genuine is False
    assert any("quickly" in reason for reason in verdict.reasons)


def test_short_but_honest_attempt_still_counts():
    """A learner does not have to hit the full target to be judged."""
    assert genuine.judge(prose(words=genuine.required_words(100))).genuine is True


def test_a_completed_drill_set_counts():
    assert genuine.judge(drills()).genuine is True


def test_mostly_skipped_drills_are_not_genuine():
    verdict = genuine.judge(drills(answered=3, total=10))
    assert verdict.genuine is False
    assert any("3 of 10" in reason for reason in verdict.reasons)


def test_drills_clicked_through_too_fast_are_not_genuine():
    assert genuine.judge(drills(seconds=5.0, answered=10, total=10)).genuine is False


def test_reasons_are_written_for_the_learner():
    """The UI shows these, so they address the learner directly."""
    for reason in genuine.judge(prose(words=0, seconds=1.0)).reasons:
        assert reason == reason.lower() or reason[0].islower() or reason.startswith("you")
        assert "metrics" not in reason
