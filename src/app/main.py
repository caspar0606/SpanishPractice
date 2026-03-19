from datetime import datetime

from src.app.score import calculate_score
from src.core.config import weak_areas, print_big_lines, print_small_lines
from src.domain.classes import ComputeStats, CurrentSession, Exercise, Progress, User
from src.core.storage import create_new_user_file, load_user_state, save_user_state
from src.domain.enums import Grammar, Tenses, Topics, ExerciseTypes, DifficultyLevels
from src.domain.preferences import grammar_preferences, tense_preferences, topic_preferences, PREFERENCES_CONFIG
from src.app.score import print_scores


def create_user(name: str) -> User:
    progress = Progress(
        tenses={tense: ComputeStats(total_attempts=0, correct_attempts=0) for tense in Tenses},
        grammar={grammar: ComputeStats(total_attempts=0, correct_attempts=0) for grammar in Grammar},
        topics={topic: ComputeStats(total_attempts=0, correct_attempts=0) for topic in Topics}
    )
    return User(name=name, progress=progress, first_time=True)


### User Selection
while True:
    print("Are you a new user (yes/no)?:")
    response = input().strip().lower()

    if response == "yes":
        user = create_user(input("Enter your new username: ").strip().lower())
        if create_new_user_file(user.name) == None:
            continue
        save_user_state(user)
        break
    
    elif response == "no":
        user = load_user_state(input("Welcome back! Please enter your username: ").strip().lower())
        if user == None:
            continue
        break
    else:
        print("Invalid input. Please enter 'yes' or 'no'.")

current_session = CurrentSession(
    user=user)

### User Progress

while True:
    print_big_lines()
    print_user_progress = input("Would you like to see your progress (yes/no)?:\n").strip().lower()

    if print_user_progress == "yes":
        print_scores(user.progress)
        break

    elif print_user_progress == "no":
        break
    else:
        print("Invalid input. Please enter 'yes' or 'no'.")

### User Exercise Selection
current_exercise = Exercise(
    start_time=datetime.now())

current_session.current_exercise = current_exercise 

while True:
    print_big_lines()
    exercise_type = input("Choose an exercise type (writing/reading): ").strip().lower()
    if exercise_type == "writing":
        current_session.current_exercise.exercise_type = ExerciseTypes.WRITING
        break
    elif exercise_type == "reading":
        current_session.current_exercise.exercise_type = ExerciseTypes.READING
        break
    else:
        print("Invalid exercise type. please select either writing or reading.")


while True:
    print_big_lines()
    weak_or_preferences = input("Do you want to focus on weak areas or your preferences (weak/preferences)?: ").strip().lower()

    if weak_or_preferences == "weak":
        print("Focusing on weak areas...")
        weak_areas_tenses, weak_areas_grammar, weak_areas_topics = weak_areas(current_session)
        
        while True:
            print_big_lines()
            difficulty_level = input("Choose a difficulty level (beginner/novice/intermediate): ").strip().lower()

            if difficulty_level == "beginner":
                current_session.current_exercise.difficulty_level = DifficultyLevels.BEGINNER
                break
            elif difficulty_level == "novice":
                current_session.current_exercise.difficulty_level = DifficultyLevels.NOVICE
                break
            elif difficulty_level == "intermediate":
                current_session.current_exercise.difficulty_level = DifficultyLevels.INTERMEDIATE
                break

            else:
                print("Invalid difficulty level. choose either 'beginner', 'novice', or 'intermediate'.")

    elif weak_or_preferences == "preferences":
        print_small_lines()
        # Logic to ask user for preferences and set focus_tenses, focus_grammar, focus_topics accordingly
        focus_tenses = tense_preferences(input(f"Enter tense preferences: \n{PREFERENCES_CONFIG[Tenses.PRESENTE_DE_INDICATIVO]} for presente de indicativo \n{PREFERENCES_CONFIG[Tenses.PRETERITO_IMPERFECTO]} for preterito imperfecto \n{PREFERENCES_CONFIG[Tenses.PRETERITO_PERFECTO_SIMPLE]} for preterito perfecto simple \n{PREFERENCES_CONFIG[Tenses.FUTURO_SIMPLE]} for futuro simple \n{PREFERENCES_CONFIG[Tenses.CONDICIONAL_SIMPLE]} for condicional simple)\n: ").strip())
        print_small_lines()
        focus_grammar = grammar_preferences(input(f"Enter grammar preferences: \n{PREFERENCES_CONFIG[Grammar.GENDER_AGREEMENT]} for gender agreement \n{PREFERENCES_CONFIG[Grammar.PLURALITY_AGREEMENT]} for plurality agreement \n{PREFERENCES_CONFIG[Grammar.POR_PARA_USAGE]} for por/para usage \n{PREFERENCES_CONFIG[Grammar.INDIRECT_DIRECT_PRONOUN_USAGE]} for indirect/direct pronoun usage \n{PREFERENCES_CONFIG[Grammar.VERB_SUBJECT_CONJUGATION]} for verb-subject conjugation\n: ").strip())
        print_small_lines()
        focus_topics = topic_preferences(input(f"Enter topic preferences: \n{PREFERENCES_CONFIG[Topics.TRAVEL]} for travel \n{PREFERENCES_CONFIG[Topics.SCHOOL]} for school \n{PREFERENCES_CONFIG[Topics.WORK]} for work \n{PREFERENCES_CONFIG[Topics.CULTURE]} for culture \n{PREFERENCES_CONFIG[Topics.CURRENT_EVENTS]} for current events \n{PREFERENCES_CONFIG[Topics.EMOTIONS]} for emotions \n{PREFERENCES_CONFIG[Topics.RELATIONSHIPS]} for relationships\n: ").strip())
        break
    else:
        print("Invalid choice. Please enter 'weak' or 'preferences'.")


