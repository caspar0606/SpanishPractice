"""The curriculum JSON is the A1→B2 roadmap; it must stay aligned with the band table."""

from src.domain.enums import Band, Grammar, Tenses, tracked_members
from src.domain.rules import band as band_rules
from src.domain.rules import curriculum as rules
from src.infrastructure.persistence.json_content import JsonContentRepository


def steps():
    return rules.parse_steps(JsonContentRepository().curriculum())


def test_every_band_has_a_step_in_order():
    bands = [step.band for step in steps()]
    assert bands == list(band_rules.BAND_ORDER)


def test_unlocks_are_monotonic():
    """A later band never retracts a concept that an earlier band introduced."""
    prev_t: set[Tenses] = set()
    prev_g: set[Grammar] = set()
    for band in band_rules.BAND_ORDER:
        tenses, grammar = rules.introduced(steps(), band)
        assert prev_t <= set(tenses)
        assert prev_g <= set(grammar)
        prev_t, prev_g = set(tenses), set(grammar)


def test_introduced_matches_what_generation_is_allowed_to_use():
    """Otherwise the recommender would drill a tense the generator refuses to emit."""
    for band in band_rules.BAND_ORDER:
        tenses, grammar = rules.introduced(steps(), band)
        assert set(tenses) == set(band_rules.allowed_tenses(band))
        assert set(grammar) == set(band_rules.allowed_grammar(band))


def test_a1_starts_with_present_and_agreement():
    tenses, grammar = rules.introduced(steps(), Band.A1)
    assert tenses == [Tenses.PRESENTE_DE_INDICATIVO]
    assert grammar == [Grammar.GENDER_AGREEMENT, Grammar.PLURALITY_AGREEMENT]


def test_a1_next_unlock_skips_the_empty_half_step():
    """A1.5 is a complexity bump, so the next named concept is the A2 pretérito."""
    nxt = rules.next_unlock(steps(), Band.A1)
    assert nxt is not None
    assert nxt.member() is Tenses.PRETERITO_PERFECTO_SIMPLE


def test_a2_introduces_both_past_tenses():
    tenses, _ = rules.introduced(steps(), Band.A2)
    assert Tenses.PRETERITO_PERFECTO_SIMPLE in tenses
    assert Tenses.PRETERITO_IMPERFECTO in tenses
    assert Tenses.FUTURO_SIMPLE not in tenses


def test_a2_next_unlock_is_the_future():
    nxt = rules.next_unlock(steps(), Band.A2)
    assert nxt is not None
    assert nxt.member() is Tenses.FUTURO_SIMPLE


def test_top_of_the_scale_has_no_next_unlock():
    assert rules.next_unlock(steps(), Band.B2) is None


def test_every_tracked_tense_and_grammar_point_appears_once():
    tenses, grammar = rules.introduced(steps(), Band.B2)
    assert set(tenses) == set(tracked_members(Tenses))
    assert set(grammar) == set(tracked_members(Grammar))
