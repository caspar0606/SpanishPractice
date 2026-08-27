from src.domain.enums import Band
from src.domain.rules.band import rank
from src.domain.rules.placement import assign_band


def test_blank_test_places_at_the_floor():
    assert assign_band(0, 8, 0.0, 0.0) is Band.A1


def test_perfect_test_places_at_the_ceiling():
    assert assign_band(8, 8, 1.0, 1.0) is Band.B2


def test_banding_is_monotonic_in_evidence():
    previous = -1
    for correct in range(0, 9):
        signal = correct / 8
        band = assign_band(correct, 8, signal, signal)
        assert rank(band) >= previous
        previous = rank(band)


def test_strong_writing_alone_cannot_leap_more_than_two_half_steps():
    """A single short sample is weak evidence, so it is capped."""
    weak_objective = assign_band(0, 8, 0.0, 0.0)
    inflated = assign_band(0, 8, 1.0, 0.0)
    assert rank(inflated) - rank(weak_objective) <= 2


def test_objective_evidence_raises_the_ceiling():
    capped = assign_band(0, 8, 1.0, 0.0)
    supported = assign_band(8, 8, 1.0, 1.0)
    assert rank(supported) > rank(capped)
