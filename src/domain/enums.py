from enum import Enum

class Tenses(str, Enum):
        PRESENTE_DE_INDICATIVO = "presente_de_indicativo"
        PRETERITO_PERFECTO_SIMPLE = "preterito_perfecto_simple"
        PRETERITO_IMPERFECTO = "preterito_imperfecto"
        FUTURO_SIMPLE = "futuro_simple"
        CONDICIONAL_SIMPLE = "condicional_simple"


class Grammar(str, Enum):
        GENDER_AGREEMENT = "gender_agreement"
        PLURALITY_AGREEMENT = "plurality_agreement"
        POR_PARA_USAGE = "por_para_usage"
        INDIRECT_DIRECT_PRONOUN_USAGE = "indirect_direct_pronoun_usage"
        VERB_SUBJECT_CONJUGATION = "verb_subject_conjugation"


class Topics(str, Enum):
        TRAVEL = "travel"
        SCHOOL = "school"
        WORK = "work"
        CULTURE = "culture"
        CURRENT_EVENTS = "current_events"
        EMOTIONS = "emotions"
        RELATIONSHIPS = "relationships"


class DifficultyLevels(str, Enum):
        BEGINNER = "beginner"
        NOVICE = "novice"
        INTERMEDIATE = "intermediate"


class ExerciseTypes(str, Enum):
        WRITING = "writing"
        READING = "reading"
        DRILLS = "drills"

class AoFs(str, Enum):
        TOPICS = "topics"
        TENSES = "tenses"
        GRAMMAR = "grammar"

class DrillTypes(str, Enum):
    SENTENCE_COMPLETION = "sentence_completion"
    TRANSLATION = "translate"
    ERROR_CORRECTION = "error_correction"
    OPTION_SELECTION = "option_selection"
