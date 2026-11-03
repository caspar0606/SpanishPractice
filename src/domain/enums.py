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
        """Legacy user-facing difficulty. Retained only to migrate v1 user files."""

        BEGINNER = "beginner"
        NOVICE = "novice"
        INTERMEDIATE = "intermediate"


class Band(str, Enum):
        """Internal proficiency band with half steps. Learners see 0–8, not these names."""

        A1 = "A1"
        A1_5 = "A1.5"
        A2 = "A2"
        A2_5 = "A2.5"
        B1 = "B1"
        B1_5 = "B1.5"
        B2 = "B2"


class Direction(str, Enum):
        """Why the learner is studying Spanish; biases exercise topics."""

        SCHOOL = "school"
        TRAVEL = "travel"
        WORK = "work"
        SOCIAL = "social"
        PERSONAL = "personal"


class WeeklyTime(str, Enum):
        """Weekly study commitment."""

        T_30_60M = "30-60m"
        T_1_2H = "1-2h"
        T_2_3H = "2-3h"
        T_4_5H = "4-5h"
        T_6_7H = "6-7h"
        T_7_PLUS = "7h+"
        T_14_PLUS = "14h+"


class LengthPreference(str, Enum):
        SHORT = "short"
        STANDARD = "standard"
        LONG = "long"


class Skill(str, Enum):
        """A trackable ability. Concept stats are keyed by skill as well."""

        WRITING = "writing"
        READING = "reading"
        LISTENING = "listening"
        SPEAKING = "speaking"
        DRILLS = "drills"


class RelativeLevel(str, Enum):
        """Task ability relative to the learner's top-level band."""

        BELOW = "below"
        AT = "at"
        ABOVE = "above"


class OnboardingStep(str, Enum):
        GOALS = "goals"
        PLACEMENT = "placement"
        READY = "ready"


class ExerciseTypes(str, Enum):
        WRITING = "writing"
        READING = "reading"
        DRILLS = "drills"
        LISTENING = "listening"
        SPEAKING = "speaking"

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


class RecommendationKind(str, Enum):
    """Why a recommender card was chosen. The UI shows these as eyebrows."""

    NEEDED = "needed"
    ROADMAP = "roadmap"
    GOAL = "goal"
    VOCAB = "vocab"
    DAILY = "daily"
    EXTRA = "extra"


class VocabStatus(str, Enum):
    NEW = "new"
    LEARNING = "learning"
    KNOWN = "known"
    IGNORED = "ignored"


class ConceptAxis(str, Enum):
    TENSE = "tense"
    GRAMMAR = "grammar"
    
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


class AgentNames(str, Enum):
    WRITING_INSTRUCTIONS = "writing_instructions"
    WRITING_TAGGING = "writing_tagging"
    WRITING_CORRECTOR = "writing_corrector"
    WRITING_SUMMARY = "writing_summary"
    READING_GENERATOR = "reading_generator"
    READING_TAGGING = "reading_tagging"
    READING_CORRECTOR = "reading_marking"
    READING_SUMMARY = "reading_summary"
    DRILLS_SENTENCE_COMPLETION_GENERATOR = "drills_sentence_completion_generator"
    DRILLS_TRANSLATION_GENERATOR = "drills_translation_generator"
    DRILLS_ERROR_CORRECTION_GENERATOR = "drills_error_correction_generator"
    DRILLS_OPTION_SELECTION_GENERATOR = "drills_option_selection_generator"
    DRILLS_OPTION_SELECTION_MARKING = "drills_option_selection_marking"
    DRILLS_ERROR_CORRECTION_MARKING = "drills_error_correction_marking"
    DRILLS_TRANSLATION_MARKING = "drills_translation_marking"
    DRILLS_SENTENCE_COMPLETION_MARKING = "drills_sentence_completion_marking"
    PLACEMENT_ASSESSOR = "placement_assessor"
    CHAT_TUTOR = "chat_tutor"
    VOCAB_EXTRACTOR = "vocab_extractor"
    LISTENING_GENERATOR = "listening_generator"
    SPEAKING_INSTRUCTIONS = "speaking_instructions"
    SPEAKING_CORRECTOR = "speaking_corrector"


CATEGORY_SENTINEL_NAMES = frozenset({"TENSES", "GRAMMAR", "TOPICS"})
CATEGORY_SENTINEL_VALUES = frozenset({"tenses", "grammar", "topics"})


def is_category_sentinel(member: Enum) -> bool:
    """True for Tenses.TENSES / Grammar.GRAMMAR / Topics.TOPICS axis labels."""
    return (
        getattr(member, "name", None) in CATEGORY_SENTINEL_NAMES
        and str(getattr(member, "value", member)) in CATEGORY_SENTINEL_VALUES
    )


def tracked_members(enum_cls: type[Enum]) -> list:
    return [member for member in enum_cls if not is_category_sentinel(member)]
