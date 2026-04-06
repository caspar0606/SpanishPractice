from datetime import datetime
from src.core.display import print_big_lines, print_small_lines, print_grammar_preferences, print_tense_preferences, print_topic_preferences
from src.core.logging import generate_id
from src.domain.enums import AoFs, Tenses, Grammar, Topics, ExerciseTypes
from src.domain.classes import AreasOfFocus, Exercise, Session, User
from src.domain.preferences import tense_preferences, topic_preferences, grammar_preferences, \
                                    TENSE_PREFERENCES_CONFIG, TOPIC_PREFERENCES_CONFIG, GRAMMAR_PREFERENCES_CONFIG, DifficultyLevels \


def exercise_selection(current_session: Session) -> Exercise:

    exercise_type = exercise_type_selection()

    difficulty_level = difficulty_selection()

    focus_grammar, focus_tenses, focus_topics = focus_selection(current_session, difficulty_level, exercise_type)

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
        start_time=datetime.now(),
        user=user,
        current_exercise=Exercise(
            id="0",
            exercise_type=ExerciseTypes.WRITING,
            difficulty_level=DifficultyLevels.BEGINNER,
            start_time=datetime.now(),
            areas_of_focus=AreasOfFocus(),
        ),
        exercise_history=[],
        progress_history=[]
    )


def exercise_type_selection() -> ExerciseTypes:
   while True:
        print_big_lines()
        try:
            return ExerciseTypes(input("Choose an exercise type (writing/reading/drills): ").strip().lower())

        except ValueError:
            print("Invalid exercise type. please select either writing, reading, or drills.")

def difficulty_selection() -> DifficultyLevels:

    print_big_lines()
    while True:
        user_difficulty_level = input("Choose a difficulty level (beginner/novice/intermediate): ").strip().lower()

        try:
            return DifficultyLevels(user_difficulty_level)
        except ValueError:
            print("Invalid difficulty level. Choose either 'beginner', 'novice', or 'intermediate'.")
        
from src.domain.user import weak_areas

def focus_selection(current_session: Session, difficulty_level: DifficultyLevels, exercise_type: ExerciseTypes):
    while True:
        print_big_lines()
        if current_session.user.first_time: 
            print("Welcome to your first Spanish Practice Session!")
            focus_grammar, focus_tenses, focus_topics = preferences_selection(exercise_type)
            return focus_grammar, focus_tenses, focus_topics

        weak_or_preferences = input("Do you want to focus on weak areas or your preferences (weak/preferences)?: ").strip().lower()
    
        if weak_or_preferences == "weak":
            focus_tenses,focus_grammar,focus_topics = weak_areas(difficulty_level, current_session.user)
            break

        elif weak_or_preferences == "preferences":
            focus_grammar, focus_tenses, focus_topics = preferences_selection(exercise_type)
            break
    
        else:
            print("Invalid choice. Please enter 'weak' or 'preferences'.")

    return focus_grammar, focus_tenses, focus_topics

def drill_selection() -> AoFs:
    while True:
        print_big_lines()
        try:
            return AoFs(input("Which area of focus (and subtopic) would you like to practice?: (topics/tenses/grammar)"))
        
        except ValueError:
            print("Invalid area of focus. Choose either 'topics', 'tenses', or 'grammar'.")


def preferences_selection(exercise_type: ExerciseTypes):

    if (exercise_type is ExerciseTypes.DRILLS):
        drill_type = drill_selection()


    while True:
        print_small_lines()
        print_tense_preferences()
        if (focus_tenses := tense_preferences(input().strip())) is None:
            continue

        print_small_lines()
        print_grammar_preferences()
        if (focus_grammar := grammar_preferences(input().strip())) is None:
            continue    
                
        print_small_lines()
        print_topic_preferences()
        if (focus_topics := topic_preferences(input().strip())) is None:
            continue
        break
    return focus_grammar, focus_tenses, focus_topics


def grammar_selection():
    print_small_lines()
    print_grammar_preferences()

    while not (focus_grammar := grammar_preferences(input().strip())): ...

    return focus_grammar

def tenses_selection():
    print_small_lines()
    print_tense_preferences()

    while not (focus_tenses := tense_preferences(input().strip())): ...

    return focus_tenses
    
def topics_selection():
    print_small_lines()
    print_topic_preferences()

    while not (focus_topics := topic_preferences(input().strip())): ...

    return focus_topics


DRILL_CONFIG = {
    AoFs.GRAMMAR: ((grammar_selection, None, None), 0),
    AoFs.TENSES: ((None, tenses_selection, None), 1),
    AoFs.TOPICS: ((None, None, topics_selection), 2)
}