import re

from pydantic import BaseModel
from src.domain.enums import DifficultyLevels, Tenses, Grammar, Topics
import re

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

TENSE_PREFERENCES_CONFIG: dict[str, str] = {
    Tenses.PRESENTE_DE_INDICATIVO: "1",
    Tenses.PRETERITO_IMPERFECTO: "2",
    Tenses.PRETERITO_PERFECTO_SIMPLE: "3",
    Tenses.FUTURO_SIMPLE: "4",
    Tenses.CONDICIONAL_SIMPLE: "5",
}
GRAMMAR_PREFERENCES_CONFIG: dict[str, str] = {
    Grammar.GENDER_AGREEMENT: "1",
    Grammar.PLURALITY_AGREEMENT: "2",
    Grammar.POR_PARA_USAGE: "3",
    Grammar.INDIRECT_DIRECT_PRONOUN_USAGE: "4",
    Grammar.VERB_SUBJECT_CONJUGATION: "5",
}

TOPIC_PREFERENCES_CONFIG: dict[str, str] = {
    Topics.TRAVEL: "1",
    Topics.SCHOOL: "2",
    Topics.WORK: "3",
    Topics.CULTURE: "4",
    Topics.CURRENT_EVENTS: "5",
    Topics.EMOTIONS: "6",
    Topics.RELATIONSHIPS: "7"
}
    


def tense_preferences(pref: str):
    if re.fullmatch(r"[1-5]+", pref) is None:
        print("Invalid number selected, please select from 1-5.")
        return None

    preferences = [
        tense
        for tense, digit in TENSE_PREFERENCES_CONFIG.items()
        if digit in pref
    ]

    print("tense preferences:", preferences)
    return preferences if preferences else None

def grammar_preferences(pref: str):
    if re.fullmatch(r"[1-5]+", pref) is None:
        print("Invalid number selected, please select from 1-5.")
        return None

    preferences = [
        grammar
        for grammar, digit in GRAMMAR_PREFERENCES_CONFIG.items()
        if digit in pref
    ]

    print("grammar preferences:", preferences)
    return preferences if preferences else None

def topic_preferences(pref: str):
    if re.fullmatch(r"[1-7]+", pref) is None:
        print("Invalid number selected, please select from 1-7.")
        return None

    preferences = [
        topic
        for topic, digit in TOPIC_PREFERENCES_CONFIG.items()
        if digit in pref
    ]

    print("topic preferences:", preferences)
    return preferences if preferences else None
