from datetime import datetime
from src.domain.rules.score import calculate_score
from src.domain.rules.config import DIFFICULTY_CONFIG
from src.infrastructure.cli.display import print_big_lines, print_small_lines, print_grammar_preferences, print_tense_preferences, print_topic_preferences
from src.infrastructure.config.logging import generate_id
from src.domain.enums import AoFs, DifficultyLevels, ExerciseStyle, ExerciseTypes, Grammar, Tenses, Topics
from src.domain.models.exercise import AreasOfFocus, Exercise, ExerciseConfig
from src.domain.models.session import ExerciseStorage, Session, User
from src.infrastructure.cli.preferences import tense_preferences, topic_preferences, grammar_preferences
from src.infrastructure.llm.contracts.shared import ExerciseContext
from src.infrastructure.persistence.file_storage import load_user_state 

def generate_exercise(username: str, type: ExerciseTypes, difficulty: 
                      DifficultyLevels, style: ExerciseStyle, preferences: AreasOfFocus | None) -> Exercise:
    
    user = load_user_state(username)

    if user is None:
        raise ValueError("{user.name} failed to fetch")
    
    if (style is ExerciseStyle.PREFERENCES):
        if preferences is None:
            raise ValueError("Preferences is incorrectly NULL")
        areas_of_focus = preferences

    else: 
        areas_of_focus = weak_areas(difficulty, user)
        
    exercise = Exercise(
        id=generate_id(),
        exercise_type=type,
        difficulty_level=difficulty,
        areas_of_focus=areas_of_focus,
        start_time=datetime.now(),
        )
    
    user.current_exercise = ExerciseStorage(
        id=exercise.id,
        type=type,
        areas_of_focus=areas_of_focus,
        exercise_config=ExerciseConfig(
            difficulty=difficulty,
            word_count=(DIFFICULTY_CONFIG[difficulty].r_word_count if type is \
            ExerciseTypes.READING else DIFFICULTY_CONFIG[difficulty].w_word_count)),
        start_time=datetime.now())

    return exercise
    


def exercise_selection(current_session: Session) -> Exercise:
    exercise_type = exercise_type_selection()

    difficulty_level = difficulty_selection()

    areas_of_focus = focus_selection(current_session, difficulty_level, exercise_type)

    exercise = Exercise(
        id=generate_id(),
        exercise_type=exercise_type,
        difficulty_level=difficulty_level,
        areas_of_focus=areas_of_focus,
        start_time=datetime.now(),
        )
    
    current_session.user.current_exercise = ExerciseStorage(
        id=exercise.id,
        type=exercise_type,
        areas_of_focus=areas_of_focus,
        exercise_config=ExerciseConfig(
            difficulty=difficulty_level,
            word_count=(DIFFICULTY_CONFIG[difficulty_level].r_word_count if exercise_type is \
            ExerciseTypes.READING else DIFFICULTY_CONFIG[difficulty_level].w_word_count)),
        start_time=datetime.now()
    )
    return exercise

def initialise_session(user: User) -> Session:
    session = Session(
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
    return session



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
        
# Determines user's weakest area based on their progress and selected difficulty level
def weak_areas(difficulty_level: DifficultyLevels, user: User) -> AreasOfFocus:
    config = DIFFICULTY_CONFIG[difficulty_level]  # type: ignore

    # Sorts tense, grammar, and topic progress by score and selects weakest k areas based on the difficulty config
    sorted_tenses = sorted(
        user.progress.tenses.items(),
        key=lambda item: calculate_score(item[1])
    )

    sorted_grammar = sorted(
        user.progress.grammar.items(),
        key=lambda item: calculate_score(item[1])
    )

    sorted_topics = sorted(
        user.progress.topics.items(),
        key=lambda item: calculate_score(item[1])
    )

    # Returns as lists of Tenses, Grammar, and Topics
    return  AreasOfFocus(focus_tenses=[Tenses(tense) for tense, _ in sorted_tenses[:config.num_tenses]], 
            focus_grammar=[Grammar(grammar) for grammar, _ in sorted_grammar[:config.num_grammar]], 
            focus_topics=[Topics(topic) for topic, _ in sorted_topics[:config.num_topics]])

def focus_selection(current_session: Session, difficulty_level: DifficultyLevels, exercise_type: ExerciseTypes) -> AreasOfFocus:
    while True:
        print_big_lines()
        if current_session.user.first_time: 
            print("Welcome to your first Spanish Practice Session!")
            areas_of_focus = preferences_selection(exercise_type)
            return areas_of_focus

        weak_or_preferences = input("Do you want to focus on weak areas or your preferences (weak/preferences)?: ").strip().lower()
    
        if weak_or_preferences == "weak":
            areas_of_focus = weak_areas(difficulty_level, current_session.user)
            break

        elif weak_or_preferences == "preferences":
            areas_of_focus = preferences_selection(exercise_type)
            break
    
        else:
            print("Invalid choice. Please enter 'weak' or 'preferences'.")

    return areas_of_focus

def drill_selection() -> AoFs:
    while True:
        print_big_lines()
        try:
            return AoFs(input("Which area of focus (and subtopic) would you like to practice?: (topics/tenses/grammar)"))
        
        except ValueError:
            print("Invalid area of focus. Choose either 'topics', 'tenses', or 'grammar'.")


def preferences_selection(exercise_type: ExerciseTypes) -> AreasOfFocus:

    if (exercise_type is ExerciseTypes.DRILLS):
        drill_type = drill_selection()
        focus_info, loc = DRILL_CONFIG[drill_type]
        list = [None, None, None]
        list[loc] = focus_info

        return AreasOfFocus(focus_grammar=list[0],focus_tenses=list[1],focus_topics=list[2])

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
    return AreasOfFocus(focus_grammar=focus_grammar, focus_tenses=focus_tenses, focus_topics=focus_topics)


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
    AoFs.GRAMMAR: [grammar_selection, 0],
    AoFs.TENSES: [tenses_selection, 1],
    AoFs.TOPICS: [topics_selection, 2]
}

def create_exercise_context(exercise: Exercise) -> ExerciseContext:
    word_count = (
        DIFFICULTY_CONFIG[exercise.difficulty_level].w_word_count
        if exercise.exercise_type == ExerciseTypes.WRITING
        else DIFFICULTY_CONFIG[exercise.difficulty_level].r_word_count
    )

    return ExerciseContext(
        areas_of_focus=exercise.areas_of_focus,
        exercise_config=ExerciseConfig(
            difficulty=exercise.difficulty_level,
            word_count=word_count)
    )