"""Deterministic placement banding.

The LLM only supplies two 0-1 signals for the writing and reading samples.
Turning those into a band is pure, conservative logic so it stays testable and
predictable.
"""

from src.domain.enums import Band
from src.domain.rules.band import BAND_ORDER, band_at_rank, rank

# Upper bound of the combined score for each band, walked in order.
_THRESHOLDS: tuple[tuple[float, Band], ...] = (
    (0.15, Band.A1),
    (0.30, Band.A1_5),
    (0.45, Band.A2),
    (0.60, Band.A2_5),
    (0.75, Band.B1),
    (0.88, Band.B1_5),
)

_MCQ_WEIGHT = 0.40
_WRITING_WEIGHT = 0.35
_READING_WEIGHT = 0.25

# A single short writing sample is weak evidence, so it may not carry the
# learner more than this many half steps above the objective evidence.
_MAX_WRITING_LIFT = 2


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def _band_for_score(score: float) -> Band:
    for ceiling, band in _THRESHOLDS:
        if score < ceiling:
            return band
    return BAND_ORDER[-1]


def combined_score(
    mcq_correct: int,
    mcq_total: int,
    writing_signal: float,
    reading_signal: float,
) -> float:
    mcq_ratio = (mcq_correct / mcq_total) if mcq_total else 0.0
    return (
        _MCQ_WEIGHT * _clamp01(mcq_ratio)
        + _WRITING_WEIGHT * _clamp01(writing_signal)
        + _READING_WEIGHT * _clamp01(reading_signal)
    )


def assign_band(
    mcq_correct: int,
    mcq_total: int,
    writing_signal: float,
    reading_signal: float,
) -> Band:
    """Round down, and cap how far the writing sample alone can lift the result."""
    proposed = _band_for_score(
        combined_score(mcq_correct, mcq_total, writing_signal, reading_signal),
    )

    # Objective evidence only: the MCQ bank plus reading comprehension.
    objective = _band_for_score(
        combined_score(mcq_correct, mcq_total, 0.0, reading_signal)
        / (_MCQ_WEIGHT + _READING_WEIGHT),
    )
    ceiling = band_at_rank(rank(objective) + _MAX_WRITING_LIFT)

    return proposed if rank(proposed) <= rank(ceiling) else ceiling
