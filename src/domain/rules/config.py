from pydantic import BaseModel

from src.domain.enums import AoFs, DifficultyLevels, DrillTypes


QUESTION_NUMBER_CONFIG = {
    DifficultyLevels.BEGINNER: {
        DrillTypes.SENTENCE_COMPLETION: 6,
        DrillTypes.OPTION_SELECTION: 7,
        DrillTypes.ERROR_CORRECTION: 4,
        DrillTypes.TRANSLATION: 3
    },
    DifficultyLevels.NOVICE: {
        DrillTypes.SENTENCE_COMPLETION: 5,
        DrillTypes.OPTION_SELECTION: 6,
        DrillTypes.ERROR_CORRECTION: 5,
        DrillTypes.TRANSLATION: 4
    },
    DifficultyLevels.INTERMEDIATE: {
        DrillTypes.SENTENCE_COMPLETION: 4,
        DrillTypes.OPTION_SELECTION: 5,
        DrillTypes.ERROR_CORRECTION: 6,
        DrillTypes.TRANSLATION: 5
    }
}

class DifficultyConfig(BaseModel):
    w_word_count: int
    r_word_count: int
    num_topics: int
    num_tenses: int
    num_grammar: int

DIFFICULTY_CONFIG: dict[DifficultyLevels, DifficultyConfig] = {
    DifficultyLevels.BEGINNER: DifficultyConfig(
        w_word_count=60,
        r_word_count=100,
        num_topics=1,
        num_tenses=1,
        num_grammar=2,
    ),
    DifficultyLevels.NOVICE: DifficultyConfig(
        w_word_count=120,
        r_word_count=250,
        num_topics=1,
        num_tenses=2,
        num_grammar=2,
    ),
    DifficultyLevels.INTERMEDIATE: DifficultyConfig(
        w_word_count=200,
        r_word_count=400,
        num_topics=2,
        num_tenses=3,
        num_grammar=3,
    ),
}

FOCUS_CONFIG = {
    "focus_tenses": (AoFs.TENSES, 0, "num_tenses"),
    "focus_grammar": (AoFs.GRAMMAR, 1, "num_grammar"),
    "focus_topics": (AoFs.TOPICS, 2, "num_topics"),
}


