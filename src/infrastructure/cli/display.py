from src.domain.enums import Grammar, Tenses, Topics
from src.infrastructure.cli.preferences import GRAMMAR_PREFERENCES_CONFIG, TENSE_PREFERENCES_CONFIG, TOPIC_PREFERENCES_CONFIG


def print_big_lines():
    print("\n" + "-"*50 + "\n")

def print_small_lines():
    print("\n" + "-"*20 + "\n")

def print_tense_preferences():
    print(f"Enter tense preferences: "
    f"\n{TENSE_PREFERENCES_CONFIG[Tenses.PRESENTE_DE_INDICATIVO]} for presente de indicativo"
    f"\n{TENSE_PREFERENCES_CONFIG[Tenses.PRETERITO_IMPERFECTO]} for preterito imperfecto " 
    f"\n{TENSE_PREFERENCES_CONFIG[Tenses.PRETERITO_PERFECTO_SIMPLE]} for preterito perfecto simple" 
    f"\n{TENSE_PREFERENCES_CONFIG[Tenses.FUTURO_SIMPLE]} for futuro simple " 
    f"\n{TENSE_PREFERENCES_CONFIG[Tenses.CONDICIONAL_SIMPLE]} for condicional simple"
    "\n: ")

def print_topic_preferences():
    print(f"Enter topic preferences: " 
                                                f"\n{TOPIC_PREFERENCES_CONFIG[Topics.TRAVEL]} for travel "
                                                f"\n{TOPIC_PREFERENCES_CONFIG[Topics.SCHOOL]} for school "
                                                f"\n{TOPIC_PREFERENCES_CONFIG[Topics.WORK]} for work "
                                                f"\n{TOPIC_PREFERENCES_CONFIG[Topics.CULTURE]} for culture "
                                                f"\n{TOPIC_PREFERENCES_CONFIG[Topics.CURRENT_EVENTS]} for current events "
                                                f"\n{TOPIC_PREFERENCES_CONFIG[Topics.EMOTIONS]} for emotions "
                                                f"\n{TOPIC_PREFERENCES_CONFIG[Topics.RELATIONSHIPS]} for relationships"
                                                "\n: ")

def print_grammar_preferences():
    print(f"Enter grammar preferences: "
                                                    f"\n{GRAMMAR_PREFERENCES_CONFIG[Grammar.GENDER_AGREEMENT]} for gender agreement"
                                                    f"\n{GRAMMAR_PREFERENCES_CONFIG[Grammar.PLURALITY_AGREEMENT]} for plurality agreement"
                                                    f"\n{GRAMMAR_PREFERENCES_CONFIG[Grammar.POR_PARA_USAGE]} for por/para usage"
                                                    f"\n{GRAMMAR_PREFERENCES_CONFIG[Grammar.INDIRECT_DIRECT_PRONOUN_USAGE]} for indirect/direct pronoun usage"
                                                    f"\n{GRAMMAR_PREFERENCES_CONFIG[Grammar.VERB_SUBJECT_CONJUGATION]} for verb-subject conjugation"
                                                    "\n: ")

