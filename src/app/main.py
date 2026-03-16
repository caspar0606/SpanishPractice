from datetime import datetime

from src.domain.classes import ComputeStats, CurrentSession, Exercise, Progress, User
from src.core.storage import create_new_user_file, load_user_state, save_user_state
from src.domain.enums import Grammar, Tenses, Topics, ExerciseTypes, DifficultyLevels


def create_user(name: str) -> User:
    progress = Progress(
        tenses={tense: ComputeStats(total_attempts=0, correct_attempts=0) for tense in Tenses},
        grammar={grammar: ComputeStats(total_attempts=0, correct_attempts=0) for grammar in Grammar},
        topics={topic: ComputeStats(total_attempts=0, correct_attempts=0) for topic in Topics}
    )
    return User(name=name, progress=progress, first_time=True)

print("Are you a new user? (yes/no)")
response = input().strip().lower()

if response == "yes":
    user = create_user(input("Enter your new username: "))
    create_new_user_file(user.name)
    save_user_state(user)

else:
    print("Welcome back! Please enter your username:")
    username = input().strip()
    user = load_user_state(username)

current_session = CurrentSession(
    user=user)

print_user_progress = input("Would you like to see your progress?(yes/no)\n").strip().lower()

if print_user_progress == "yes":
    from src.app.score import print_scores
    print_scores(user.progress)

else:
    print("Let's get started with some exercises!")

current_exercise = Exercise(
    start_time=datetime.now())

current_session.current_exercise = current_exercise 

exercise_type = input("Choose an exercise type (writing/speaking): ").strip().lower()
if exercise_type == "writing":
    current_session.current_exercise.exercise_type = ExerciseTypes.WRITING
elif exercise_type == "speaking":
    current_session.current_exercise.exercise_type = ExerciseTypes.SPEAKING

difficulty_level = input("Choose a difficulty level (beginner/novice/intermediate): ").strip().lower()
if difficulty_level == "beginner":
    current_session.current_exercise.difficulty_level = DifficultyLevels.BEGINNER
elif difficulty_level == "novice":
    current_session.current_exercise.difficulty_level = DifficultyLevels.NOVICE
elif difficulty_level == "intermediate":
    current_session.current_exercise.difficulty_level = DifficultyLevels.INTERMEDIATE








