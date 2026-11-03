"""Decides whether a submission counts as evidence of ability.

Blank, one-word, or instantly-submitted attempts still get marked and still
show feedback, but they must not move the learner's band. Reasons are phrased
for the learner because the UI shows them.
"""

from src.domain.models.exercise import AttemptMetrics, GenuineVerdict

MIN_SECONDS = 15.0
MIN_WORDS = 8
MIN_WORD_RATIO = 0.35
MIN_ANSWERED_RATIO = 0.6
MIN_SECONDS_PER_ITEM = 3.0


def required_words(target_words: int) -> int:
    """Enough to show real effort, well below the full target."""
    return max(MIN_WORDS, round(target_words * MIN_WORD_RATIO))


def judge(metrics: AttemptMetrics) -> GenuineVerdict:
    reasons: list[str] = []

    if metrics.items_total > 0:
        answered_ratio = metrics.items_answered / metrics.items_total
        if answered_ratio < MIN_ANSWERED_RATIO:
            reasons.append(
                f"you answered {metrics.items_answered} of {metrics.items_total} questions",
            )
        if metrics.seconds_spent < metrics.items_total * MIN_SECONDS_PER_ITEM:
            reasons.append("this was submitted too quickly to have read the questions")
    else:
        needed = required_words(metrics.target_words)
        if metrics.response_words < needed:
            reasons.append(
                f"your response was {metrics.response_words} words, and we need about {needed} to judge it",
            )
        if metrics.seconds_spent < MIN_SECONDS:
            reasons.append("this was submitted too quickly to be a full attempt")

    return GenuineVerdict(genuine=not reasons, reasons=reasons)
