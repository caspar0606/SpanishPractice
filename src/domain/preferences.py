from pydantic import BaseModel
from src.domain.enums import DifficultyLevels, Tenses, Grammar, Topics

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

PREFERENCES_CONFIG: dict[str, str] = {
    Tenses.PRESENTE_DE_INDICATIVO: "1",
    Tenses.PRETERITO_IMPERFECTO: "2",
    Tenses.PRETERITO_PERFECTO_SIMPLE: "3",
    Tenses.FUTURO_SIMPLE: "4",
    Tenses.CONDICIONAL_SIMPLE: "5",

    Grammar.GENDER_AGREEMENT: "1",
    Grammar.PLURALITY_AGREEMENT: "2",
    Grammar.POR_PARA_USAGE: "3",
    Grammar.INDIRECT_DIRECT_PRONOUN_USAGE: "4",
    Grammar.VERB_SUBJECT_CONJUGATION: "5",

    Topics.TRAVEL: "1",
    Topics.SCHOOL: "2",
    Topics.WORK: "3",
    Topics.CULTURE: "4",
    Topics.CURRENT_EVENTS: "5",
    Topics.EMOTIONS: "6",
    Topics.RELATIONSHIPS: "7"
}
    



def tense_preferences(pref: str):
    preferences = []
    if PREFERENCES_CONFIG[Tenses.PRESENTE_DE_INDICATIVO] in pref:
        preferences.append(Tenses.PRESENTE_DE_INDICATIVO)
    elif PREFERENCES_CONFIG[Tenses.PRETERITO_IMPERFECTO] in pref:
        preferences.append(Tenses.PRETERITO_IMPERFECTO)
    elif PREFERENCES_CONFIG[Tenses.PRETERITO_PERFECTO_SIMPLE] in pref:
        preferences.append(Tenses.PRETERITO_PERFECTO_SIMPLE)
    elif PREFERENCES_CONFIG[Tenses.FUTURO_SIMPLE] in pref:
        preferences.append(Tenses.FUTURO_SIMPLE)
    elif PREFERENCES_CONFIG[Tenses.CONDICIONAL_SIMPLE] in pref:
        preferences.append(Tenses.CONDICIONAL_SIMPLE)
    else:
        print("Invalid input, no tense preferences selected.")
        return None

    return preferences
    
def grammar_preferences(pref: str) -> list[Grammar]:
    preferences = []
    if PREFERENCES_CONFIG[Grammar.GENDER_AGREEMENT] in pref:
        preferences.append(Grammar.GENDER_AGREEMENT)
    elif PREFERENCES_CONFIG[Grammar.PLURALITY_AGREEMENT] in pref:
        preferences.append(Grammar.PLURALITY_AGREEMENT)
    elif PREFERENCES_CONFIG[Grammar.POR_PARA_USAGE] in pref:
        preferences.append(Grammar.POR_PARA_USAGE)
    elif PREFERENCES_CONFIG[Grammar.INDIRECT_DIRECT_PRONOUN_USAGE] in pref:
        preferences.append(Grammar.INDIRECT_DIRECT_PRONOUN_USAGE)
    elif PREFERENCES_CONFIG[Grammar.VERB_SUBJECT_CONJUGATION] in pref:
        preferences.append(Grammar.VERB_SUBJECT_CONJUGATION)
    else:
        print("Invalid input, no grammar preferences selected.")

    return preferences
    
def topic_preferences(pref: str) -> list[Topics]:
    preferences = []
    if PREFERENCES_CONFIG[Topics.TRAVEL] in pref:
        preferences.append(Topics.TRAVEL)
    elif PREFERENCES_CONFIG[Topics.SCHOOL] in pref:
        preferences.append(Topics.SCHOOL)
    elif PREFERENCES_CONFIG[Topics.WORK] in pref:
        preferences.append(Topics.WORK)
    elif PREFERENCES_CONFIG[Topics.CULTURE] in pref:
        preferences.append(Topics.CULTURE)
    elif PREFERENCES_CONFIG[Topics.CURRENT_EVENTS] in pref:
        preferences.append(Topics.CURRENT_EVENTS)
    elif PREFERENCES_CONFIG[Topics.EMOTIONS]     in pref:
        preferences.append(Topics.EMOTIONS)
    elif PREFERENCES_CONFIG[Topics.RELATIONSHIPS] in pref:
        preferences.append(Topics.RELATIONSHIPS)
    else:
        print("Invalid input, no topic preferences selected.")

    return preferences