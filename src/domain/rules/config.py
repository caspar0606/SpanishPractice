from src.domain.enums import AoFs, Band, DrillTypes

# Drill counts per band. Lower bands get more mechanical items, higher bands
# fewer but harder ones.
QUESTION_NUMBER_CONFIG: dict[Band, dict[DrillTypes, int]] = {
    Band.A1: {
        DrillTypes.SENTENCE_COMPLETION: 6,
        DrillTypes.OPTION_SELECTION: 7,
        DrillTypes.ERROR_CORRECTION: 3,
        DrillTypes.TRANSLATION: 3,
    },
    Band.A1_5: {
        DrillTypes.SENTENCE_COMPLETION: 6,
        DrillTypes.OPTION_SELECTION: 7,
        DrillTypes.ERROR_CORRECTION: 4,
        DrillTypes.TRANSLATION: 3,
    },
    Band.A2: {
        DrillTypes.SENTENCE_COMPLETION: 5,
        DrillTypes.OPTION_SELECTION: 6,
        DrillTypes.ERROR_CORRECTION: 5,
        DrillTypes.TRANSLATION: 4,
    },
    Band.A2_5: {
        DrillTypes.SENTENCE_COMPLETION: 5,
        DrillTypes.OPTION_SELECTION: 6,
        DrillTypes.ERROR_CORRECTION: 5,
        DrillTypes.TRANSLATION: 4,
    },
    Band.B1: {
        DrillTypes.SENTENCE_COMPLETION: 4,
        DrillTypes.OPTION_SELECTION: 5,
        DrillTypes.ERROR_CORRECTION: 6,
        DrillTypes.TRANSLATION: 5,
    },
    Band.B1_5: {
        DrillTypes.SENTENCE_COMPLETION: 4,
        DrillTypes.OPTION_SELECTION: 5,
        DrillTypes.ERROR_CORRECTION: 6,
        DrillTypes.TRANSLATION: 5,
    },
    Band.B2: {
        DrillTypes.SENTENCE_COMPLETION: 4,
        DrillTypes.OPTION_SELECTION: 5,
        DrillTypes.ERROR_CORRECTION: 6,
        DrillTypes.TRANSLATION: 6,
    },
}

FOCUS_CONFIG = {
    "focus_tenses": (AoFs.TENSES, 0, "num_tenses"),
    "focus_grammar": (AoFs.GRAMMAR, 1, "num_grammar"),
    "focus_topics": (AoFs.TOPICS, 2, "num_topics"),
}
