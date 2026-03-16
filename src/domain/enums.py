from enum import Enum

from pydantic import BaseModel

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
        SPEAKING = "speaking"



class DifficultyConfig(BaseModel):
    word_count: int
    num_topics: int
    num_tenses: int
    num_grammar: int


DIFFICULTY_CONFIG: dict[DifficultyLevels, DifficultyConfig] = {
    DifficultyLevels.BEGINNER: DifficultyConfig(
        word_count=60,
        num_topics=1,
        num_tenses=1,
        num_grammar=2,
    ),
    DifficultyLevels.NOVICE: DifficultyConfig(
        word_count=120,
        num_topics=1,
        num_tenses=2,
        num_grammar=3,
    ),
    DifficultyLevels.INTERMEDIATE: DifficultyConfig(
        word_count=200,
        num_topics=2,
        num_tenses=3,
        num_grammar=4,
    ),
}
