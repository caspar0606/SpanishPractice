from enum import Enum

class Tenses(str, Enum):
        TENSES = "tenses"
        PRESENTE_DE_INDICATIVO = "presente_de_indicativo"
        PRETERITO_PERFECTO_SIMPLE = "preterito_perfecto_simple"
        PRETERITO_IMPERFECTO = "preterito_imperfecto"
        FUTURO_SIMPLE = "futuro_simple"
        CONDICIONAL_SIMPLE = "condicional_simple"


class Grammar(str, Enum):
        GRAMMAR = "grammar"
        GENDER_AGREEMENT = "gender_agreement"
        PLURALITY_AGREEMENT = "plurality_agreement"
        POR_PARA_USAGE = "por_para_usage"
        INDIRECT_DIRECT_PRONOUN_USAGE = "indirect_direct_pronoun_usage"
        VERB_SUBJECT_CONJUGATION = "verb_subject_conjugation"


class Topics(str, Enum):
        TOPICS = "topics"
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
    TRANSLATION = "translation"
    ERROR_CORRECTION = "error_correction"
    OPTION_SELECTION = "option_selection"

class ExerciseStyle(str, Enum):
    WEAKNESSES = "weaknesses"
    PREFERENCES = "preferences"
    
class Times(str, Enum):
       PAST = "past"
       PRESENT = "present"
       FUTURE = "future"

class Aspects(str, Enum):
       SIMPLE = "simple"
       PERFECT = "perfect"
       PROGRESSIVE = "progressive"

class Moods(str, Enum):
       SUBJUNCTIVE = "subjunctive"
       INDICATIVE = "indicative" 

# Tenses.TENSES, Grammar.GRAMMAR and Topics.TOPICS name their own category rather
# than a practisable area. They are retained so user files saved before they were
# excluded still validate, but they must never be tracked in progress or offered as
# an area of focus. Use practice_members() anywhere a real area is required.
_CATEGORY_SENTINEL_VALUES = frozenset({"tenses", "grammar", "topics"})

FOCUS_ENUMS = (Tenses, Grammar, Topics)


def is_category_sentinel(member: object) -> bool:
    """True for the self-naming sentinel member of Tenses, Grammar or Topics."""
    return isinstance(member, FOCUS_ENUMS) and member.value in _CATEGORY_SENTINEL_VALUES


def practice_members(enum_cls: type[Enum]) -> list[Enum]:
    """Members of a focus enum that a learner can actually practise."""
    return [member for member in enum_cls if not is_category_sentinel(member)]
