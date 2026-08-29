"""Band-driven exercise difficulty.

The learner's proficiency band is the single source of difficulty. Nothing
user-facing selects a raw difficulty level any more.
"""

from pydantic import BaseModel

from src.domain.enums import (
    Band,
    DifficultyLevels,
    ExerciseTypes,
    Grammar,
    LengthPreference,
    Tenses,
    WeeklyTime,
)

# Ordered low to high; index is the band's rank.
BAND_ORDER: tuple[Band, ...] = (
    Band.A1,
    Band.A1_5,
    Band.A2,
    Band.A2_5,
    Band.B1,
    Band.B1_5,
    Band.B2,
)

# Learner-facing 0–8 scale. Internal Band values stay A1…B2 for storage.
# 0 and 1 are reserved (complete beginner / first phrases); the app starts at 2.
DISPLAY_LEVEL: dict[Band, int] = {
    Band.A1: 2,
    Band.A1_5: 3,
    Band.A2: 4,
    Band.A2_5: 5,
    Band.B1: 6,
    Band.B1_5: 7,
    Band.B2: 8,
}


class BandConfig(BaseModel):
    gloss: str
    cefr_hint: str
    w_word_count: int
    r_word_count: int
    l_word_count: int
    num_topics: int
    num_tenses: int
    num_grammar: int
    allowed_tenses: list[Tenses]
    allowed_grammar: list[Grammar]


_A1_TENSES = [Tenses.PRESENTE_DE_INDICATIVO]
_A2_TENSES = _A1_TENSES + [Tenses.PRETERITO_PERFECTO_SIMPLE, Tenses.PRETERITO_IMPERFECTO]
_A2_5_TENSES = _A2_TENSES + [Tenses.FUTURO_SIMPLE]
_B1_TENSES = _A2_5_TENSES + [Tenses.CONDICIONAL_SIMPLE]

_A1_GRAMMAR = [Grammar.GENDER_AGREEMENT, Grammar.PLURALITY_AGREEMENT]
_A2_GRAMMAR = _A1_GRAMMAR + [Grammar.VERB_SUBJECT_CONJUGATION]
_A2_5_GRAMMAR = _A2_GRAMMAR + [Grammar.POR_PARA_USAGE]
_B1_GRAMMAR = _A2_5_GRAMMAR + [Grammar.INDIRECT_DIRECT_PRONOUN_USAGE]


BAND_CONFIG: dict[Band, BandConfig] = {
    Band.A1: BandConfig(
        gloss="first words and phrases",
        cefr_hint="Level 2 of 8: very simple vocabulary, short present-tense sentences, concrete ideas.",
        w_word_count=50,
        r_word_count=90,
        l_word_count=60,
        num_topics=1,
        num_tenses=1,
        num_grammar=1,
        allowed_tenses=_A1_TENSES,
        allowed_grammar=_A1_GRAMMAR,
    ),
    Band.A1_5: BandConfig(
        gloss="getting by with the basics",
        cefr_hint="Level 3 of 8: simple everyday vocabulary, short sentences, mostly present tense.",
        w_word_count=70,
        r_word_count=120,
        l_word_count=80,
        num_topics=1,
        num_tenses=1,
        num_grammar=2,
        allowed_tenses=_A1_TENSES,
        allowed_grammar=_A1_GRAMMAR,
    ),
    Band.A2: BandConfig(
        gloss="basic conversational Spanish",
        cefr_hint="Level 4 of 8: common vocabulary, simple past and present, mostly simple sentences.",
        w_word_count=100,
        r_word_count=180,
        l_word_count=110,
        num_topics=1,
        num_tenses=2,
        num_grammar=2,
        allowed_tenses=_A2_TENSES,
        allowed_grammar=_A2_GRAMMAR,
    ),
    Band.A2_5: BandConfig(
        gloss="confident with the basics",
        cefr_hint="Level 5 of 8: common vocabulary with some variety, past, present and future.",
        w_word_count=130,
        r_word_count=240,
        l_word_count=140,
        num_topics=1,
        num_tenses=2,
        num_grammar=2,
        allowed_tenses=_A2_5_TENSES,
        allowed_grammar=_A2_5_GRAMMAR,
    ),
    Band.B1: BandConfig(
        gloss="solid conversational Spanish",
        cefr_hint="Level 6 of 8: clear structure, richer but still common vocabulary, all core tenses.",
        w_word_count=170,
        r_word_count=320,
        l_word_count=180,
        num_topics=2,
        num_tenses=3,
        num_grammar=3,
        allowed_tenses=_B1_TENSES,
        allowed_grammar=_B1_GRAMMAR,
    ),
    Band.B1_5: BandConfig(
        gloss="comfortable in most everyday situations",
        cefr_hint="Level 7 of 8: longer connected text, natural phrasing, all core tenses used well.",
        w_word_count=210,
        r_word_count=400,
        l_word_count=220,
        num_topics=2,
        num_tenses=3,
        num_grammar=3,
        allowed_tenses=_B1_TENSES,
        allowed_grammar=_B1_GRAMMAR,
    ),
    Band.B2: BandConfig(
        gloss="upper intermediate",
        cefr_hint="Level 8 of 8: extended, well-organised text with nuanced vocabulary and complex sentences.",
        w_word_count=260,
        r_word_count=480,
        l_word_count=260,
        num_topics=2,
        num_tenses=4,
        num_grammar=4,
        allowed_tenses=_B1_TENSES,
        allowed_grammar=_B1_GRAMMAR,
    ),
}


LENGTH_MULTIPLIER: dict[LengthPreference, float] = {
    LengthPreference.SHORT: 0.7,
    LengthPreference.STANDARD: 1.0,
    LengthPreference.LONG: 1.3,
}


# Rough published CEFR guided-study hours to advance one half step.
_HOURS_PER_HALF_STEP: dict[Band, int] = {
    Band.A1: 40,
    Band.A1_5: 40,
    Band.A2: 50,
    Band.A2_5: 50,
    Band.B1: 70,
    Band.B1_5: 70,
    Band.B2: 90,
}

_WEEKLY_HOURS: dict[WeeklyTime, float] = {
    WeeklyTime.T_30_60M: 0.75,
    WeeklyTime.T_1_2H: 1.5,
    WeeklyTime.T_2_3H: 2.5,
    WeeklyTime.T_4_5H: 4.5,
    WeeklyTime.T_6_7H: 6.5,
    WeeklyTime.T_7_PLUS: 9.0,
    WeeklyTime.T_14_PLUS: 16.0,
}

# v1 files stored a user-selected difficulty; map it to the nearest band.
_LEGACY_DIFFICULTY_TO_BAND: dict[DifficultyLevels, Band] = {
    DifficultyLevels.BEGINNER: Band.A1,
    DifficultyLevels.NOVICE: Band.A2,
    DifficultyLevels.INTERMEDIATE: Band.B1,
}


def config_for(band: Band) -> BandConfig:
    return BAND_CONFIG[band]


def cefr_hint(band: Band) -> str:
    return BAND_CONFIG[band].cefr_hint


def gloss(band: Band) -> str:
    return BAND_CONFIG[band].gloss


def display_level(band: Band) -> int:
    """Loose 0–8 number shown to learners. Not an official CEFR grade."""
    return DISPLAY_LEVEL[band]


def rank(band: Band) -> int:
    return BAND_ORDER.index(band)


def band_at_rank(index: int) -> Band:
    clamped = max(0, min(index, len(BAND_ORDER) - 1))
    return BAND_ORDER[clamped]


def shift(band: Band, steps: int) -> Band:
    """Move a whole number of half steps, clamped to the band range."""
    return band_at_rank(rank(band) + steps)


def is_above(band: Band, other: Band) -> bool:
    return rank(band) > rank(other)


def legacy_difficulty_to_band(value: object) -> Band:
    try:
        return _LEGACY_DIFFICULTY_TO_BAND[DifficultyLevels(value)]
    except (ValueError, KeyError):
        return Band.A1


def word_count_for(
    exercise_type: ExerciseTypes,
    band: Band,
    length: LengthPreference = LengthPreference.STANDARD,
) -> int:
    """Target word count for generated material. 0 where length is meaningless."""
    config = BAND_CONFIG[band]
    if exercise_type is ExerciseTypes.READING:
        base = config.r_word_count
    elif exercise_type is ExerciseTypes.WRITING:
        base = config.w_word_count
    elif exercise_type is ExerciseTypes.LISTENING:
        base = config.l_word_count
    elif exercise_type is ExerciseTypes.SPEAKING:
        # Spoken answers are shorter than written ones.
        base = max(30, int(config.w_word_count * 0.5))
    else:
        return 0
    return max(20, round(base * LENGTH_MULTIPLIER[length]))


def focus_counts(band: Band) -> tuple[int, int, int]:
    """How many tenses, grammar points, and topics to target at this band."""
    config = BAND_CONFIG[band]
    return config.num_tenses, config.num_grammar, config.num_topics


def allowed_tenses(band: Band) -> list[Tenses]:
    return list(BAND_CONFIG[band].allowed_tenses)


def allowed_grammar(band: Band) -> list[Grammar]:
    return list(BAND_CONFIG[band].allowed_grammar)


def hours_to_next_band(band: Band, weekly: WeeklyTime) -> int:
    """Rough weeks-to-next-half-step, from published CEFR hour ranges."""
    hours = _HOURS_PER_HALF_STEP[band]
    per_week = _WEEKLY_HOURS[weekly]
    return max(1, round(hours / per_week))
