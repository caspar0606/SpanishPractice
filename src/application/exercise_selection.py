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
from src.infrastructure.persistence.file_storage import load_user_state, save_user_state

def generate_exercise(username: str, type: ExerciseTypes, difficulty: 
                      DifficultyLevels, style: ExerciseStyle, preferences: AreasOfFocus | None) -> Exercise:
    
    user = load_user_state(username)

    if user is None:
        raise ValueError(f"User '{username}' not found")
    
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

    save_user_state(user)
    return exercise





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