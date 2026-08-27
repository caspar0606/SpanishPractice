from src.domain.enums import Band, ExerciseTypes, LengthPreference, WeeklyTime
from src.domain.rules import band as band_rules


def test_band_order_is_monotonic():
    ranks = [band_rules.rank(band) for band in band_rules.BAND_ORDER]
    assert ranks == sorted(ranks)
    assert len(set(ranks)) == len(band_rules.BAND_ORDER)


def test_every_band_has_config():
    for band in Band:
        config = band_rules.config_for(band)
        assert config.w_word_count > 0
        assert config.cefr_hint
        assert config.gloss
        assert config.allowed_tenses
        assert config.allowed_grammar


def test_gloss_does_not_repeat_the_band_name():
    """The UI renders "{band} — {gloss}", so the gloss must stand alone."""
    for band in Band:
        gloss = band_rules.gloss(band)
        assert band.value not in gloss
        assert "—" not in gloss


def test_word_counts_increase_with_band():
    counts = [
        band_rules.word_count_for(ExerciseTypes.WRITING, band)
        for band in band_rules.BAND_ORDER
    ]
    assert counts == sorted(counts)
    assert counts[0] < counts[-1]


def test_length_preference_scales_word_count():
    short = band_rules.word_count_for(ExerciseTypes.READING, Band.B1, LengthPreference.SHORT)
    standard = band_rules.word_count_for(ExerciseTypes.READING, Band.B1, LengthPreference.STANDARD)
    long_ = band_rules.word_count_for(ExerciseTypes.READING, Band.B1, LengthPreference.LONG)
    assert short < standard < long_


def test_drills_have_no_word_count():
    assert band_rules.word_count_for(ExerciseTypes.DRILLS, Band.B1) == 0


def test_allowed_concepts_grow_with_band():
    assert len(band_rules.allowed_tenses(Band.A1)) < len(band_rules.allowed_tenses(Band.B1))
    assert len(band_rules.allowed_grammar(Band.A1)) < len(band_rules.allowed_grammar(Band.B1))


def test_shift_clamps_at_both_ends():
    assert band_rules.shift(Band.A1, -5) is Band.A1
    assert band_rules.shift(Band.B2, 5) is Band.B2
    assert band_rules.shift(Band.A2, 1) is Band.A2_5


def test_more_study_time_means_fewer_weeks():
    slow = band_rules.hours_to_next_band(Band.A2, WeeklyTime.T_30_60M)
    fast = band_rules.hours_to_next_band(Band.A2, WeeklyTime.T_14_PLUS)
    assert slow > fast >= 1
