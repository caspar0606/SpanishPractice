from datetime import datetime
from src.core.display import print_big_lines, print_small_lines
from src.core.logging import generate_id
from src.domain.user import weak_areas
from src.domain.enums import Tenses, Grammar, Topics, ExerciseTypes
from src.domain.classes import AreasOfFocus, Exercise, Session, User
from src.domain.preferences import tense_preferences, topic_preferences, grammar_preferences, \
                                    TENSE_PREFERENCES_CONFIG, TOPIC_PREFERENCES_CONFIG, GRAMMAR_PREFERENCES_CONFIG, DifficultyLevels

def exercise_selection(current_session: Session) -> Exercise:

    exercise_type = exercise_type_selection()

    difficulty_level = difficulty_selection()

    focus_grammar, focus_tenses, focus_topics = focus_selection(current_session, difficulty_level)

    return Exercise(
        id=generate_id(),
        exercise_type=exercise_type,
        difficulty_level=difficulty_level,
        areas_of_focus=AreasOfFocus(
            focus_grammar=focus_grammar,
            focus_tenses=focus_tenses,
            focus_topics=focus_topics),
        start_time=datetime.now(),
        )

def initialise_session(user: User) -> Session:
    return Session(
        id=generate_id(),
        user=user,
        current_exercise=Exercise(
            id="0",
            exercise_type=ExerciseTypes.WRITING,
            difficulty_level=DifficultyLevels.BEGINNER,
            start_time=datetime.now(),
            areas_of_focus=AreasOfFocus()
        )
    )


def exercise_type_selection() -> ExerciseTypes:
   while True:
        print_big_lines()
        exercise_type = input("Choose an exercise type (writing/reading): ").strip().lower()
        if exercise_type == "writing":
            exercise_type = ExerciseTypes.WRITING
            return exercise_type

        elif exercise_type == "reading":
            exercise_type = ExerciseTypes.READING
            return exercise_type
        
        else:
            print("Invalid exercise type. please select either writing or reading.")



def difficulty_selection() -> DifficultyLevels:

    print_big_lines()
    while True:
        user_difficulty_level = input("Choose a difficulty level (beginner/novice/intermediate): ").strip().lower()

        try:
            return DifficultyLevels(user_difficulty_level)
        except ValueError:
            print("Invalid difficulty level. Choose either 'beginner', 'novice', or 'intermediate'.")
        


def focus_selection(current_session: Session, difficulty_level: DifficultyLevels):
    while True:
        print_big_lines()
        if current_session.user.first_time: 
            print("Welcome to your first Spanish Practice Session!")
            focus_grammar, focus_tenses, focus_topics = preferences_selection()
            return focus_grammar, focus_tenses, focus_topics

        weak_or_preferences = input("Do you want to focus on weak areas or your preferences (weak/preferences)?: ").strip().lower()
    
        if weak_or_preferences == "weak":
            focus_tenses,focus_grammar,focus_topics = weak_areas(difficulty_level, current_session.user)
            break

        elif weak_or_preferences == "preferences":
            focus_grammar, focus_tenses, focus_topics = preferences_selection()
            break
    
        else:
            print("Invalid choice. Please enter 'weak' or 'preferences'.")

    return focus_grammar, focus_tenses, focus_topics



def preferences_selection():
    while True:
        print_small_lines()
        if (focus_tenses := tense_preferences(input(f"Enter tense preferences: "
                                                f"\n{TENSE_PREFERENCES_CONFIG[Tenses.PRESENTE_DE_INDICATIVO]} for presente de indicativo"
                                                f"\n{TENSE_PREFERENCES_CONFIG[Tenses.PRETERITO_IMPERFECTO]} for preterito imperfecto " 
                                                f"\n{TENSE_PREFERENCES_CONFIG[Tenses.PRETERITO_PERFECTO_SIMPLE]} for preterito perfecto simple" 
                                                f"\n{TENSE_PREFERENCES_CONFIG[Tenses.FUTURO_SIMPLE]} for futuro simple " 
                                                f"\n{TENSE_PREFERENCES_CONFIG[Tenses.CONDICIONAL_SIMPLE]} for condicional simple"
                                                "\n: ").strip())) is None:
            continue
        print_small_lines()
        if (focus_grammar := grammar_preferences(input(f"Enter grammar preferences: "
                                                    f"\n{GRAMMAR_PREFERENCES_CONFIG[Grammar.GENDER_AGREEMENT]} for gender agreement"
                                                    f"\n{GRAMMAR_PREFERENCES_CONFIG[Grammar.PLURALITY_AGREEMENT]} for plurality agreement"
                                                    f"\n{GRAMMAR_PREFERENCES_CONFIG[Grammar.POR_PARA_USAGE]} for por/para usage"
                                                    f"\n{GRAMMAR_PREFERENCES_CONFIG[Grammar.INDIRECT_DIRECT_PRONOUN_USAGE]} for indirect/direct pronoun usage"
                                                    f"\n{GRAMMAR_PREFERENCES_CONFIG[Grammar.VERB_SUBJECT_CONJUGATION]} for verb-subject conjugation"
                                                    "\n: ").strip())) is None:
            continue    
                
        print_small_lines()
        if (focus_topics := topic_preferences(input(f"Enter topic preferences: " 
                                                f"\n{TOPIC_PREFERENCES_CONFIG[Topics.TRAVEL]} for travel "
                                                f"\n{TOPIC_PREFERENCES_CONFIG[Topics.SCHOOL]} for school "
                                                f"\n{TOPIC_PREFERENCES_CONFIG[Topics.WORK]} for work "
                                                f"\n{TOPIC_PREFERENCES_CONFIG[Topics.CULTURE]} for culture "
                                                f"\n{TOPIC_PREFERENCES_CONFIG[Topics.CURRENT_EVENTS]} for current events "
                                                f"\n{TOPIC_PREFERENCES_CONFIG[Topics.EMOTIONS]} for emotions "
                                                f"\n{TOPIC_PREFERENCES_CONFIG[Topics.RELATIONSHIPS]} for relationships"
                                                "\n: ").strip())) is None:
            continue
        break
    return focus_grammar, focus_tenses, focus_topics
