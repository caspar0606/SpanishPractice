from datetime import datetime

from src.app.score import calculate_score
from src.core.config import weak_areas
from src.domain.classes import ComputeStats, CurrentSession, Exercise, Progress, User
from src.core.storage import create_new_user_file, load_user_state, save_user_state
from src.domain.enums import Grammar, Tenses, Topics, ExerciseTypes, DifficultyLevels, DIFFICULTY_CONFIG


def create_user(name: str) -> User:
    progress = Progress(
        tenses={tense: ComputeStats(total_attempts=0, correct_attempts=0) for tense in Tenses},
        grammar={grammar: ComputeStats(total_attempts=0, correct_attempts=0) for grammar in Grammar},
        topics={topic: ComputeStats(total_attempts=0, correct_attempts=0) for topic in Topics}
    )
    return User(name=name, progress=progress, first_time=True)


### User Selection
print("Are you a new user? (yes/no)")
response = input().strip().lower()

if response == "yes":
    user = create_user(input("Enter your new username: ").strip().lower())
    create_new_user_file(user.name)
    save_user_state(user)

else:
    print("Welcome back! Please enter your username:")
    username = input().strip().lower()
    user = load_user_state(username)

current_session = CurrentSession(
    user=user)

### User Progress
print_user_progress = input("Would you like to see your progress? (yes/no)\n").strip().lower()

if print_user_progress == "yes":
    from src.app.score import print_scores
    print_scores(user.progress)

else:
    print("Let's get started with some exercises!")

### User Exercise Selection
current_exercise = Exercise(
    start_time=datetime.now())

current_session.current_exercise = current_exercise 

exercise_type = input("Choose an exercise type (writing/speaking): ").strip().lower()
if exercise_type == "writing":
    current_session.current_exercise.exercise_type = ExerciseTypes.WRITING
elif exercise_type == "speaking":
    current_session.current_exercise.exercise_type = ExerciseTypes.SPEAKING
else:
    print("Invalid exercise type. Defaulting to writing.")
    current_session.current_exercise.exercise_type = ExerciseTypes.WRITING

weak_or_preferences = input("Do you want to focus on weak areas or your preferences? (weak/preferences) ").strip().lower()

if weak_or_preferences == "weak":
    print("Focusing on weak areas...")
    weak_areas_tenses, weak_areas_grammar, weak_areas_topics = weak_areas(current_session)
    # Logic to determine weak areas and set focus_tenses, focus_grammar, focus_topics accordingly
elif weak_or_preferences == "preferences":
    print("Focusing on your preferences...")
    # Logic to ask user for preferences and set focus_tenses, focus_grammar, focus_topics accordingly

difficulty_level = input("Choose a difficulty level (beginner/novice/intermediate): ").strip().lower()

if difficulty_level == "beginner":
    current_session.current_exercise.difficulty_level = DifficultyLevels.BEGINNER
elif difficulty_level == "novice":
    current_session.current_exercise.difficulty_level = DifficultyLevels.NOVICE
elif difficulty_level == "intermediate":
    current_session.current_exercise.difficulty_level = DifficultyLevels.INTERMEDIATE
else:
    print("Invalid difficulty level. Defaulting to beginner.")
    current_session.current_exercise.difficulty_level = DifficultyLevels.BEGINNER


