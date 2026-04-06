from src.domain.models.exercise import Exercise, ExerciseStorage
from src.domain.models.user import User
from src.infrastructure.persistence.file_storage import load_user_state


def user_from_name(username: str) -> User:
    user = load_user_state(username)

    if user is None:
        raise ValueError(f"User '{username}' not found")

    if user.current_exercise is None:
        raise ValueError(f"User '{username}' has no current session")

    exercise = user.current_exercise
    if exercise is None:
        raise ValueError(f"User '{username}' has no current exercise")

    return user

def storage_to_exercise(storage: ExerciseStorage) -> Exercise:

    return Exercise(
        id=storage.id,
        exercise_type=storage.type,
        difficulty_level=storage.exercise_config.difficulty,
        areas_of_focus=storage.areas_of_focus,
        start_time=storage.start_time
    )

def user_exercise_cache(username: str) -> tuple[User, Exercise]:
    user = user_from_name(username)

    if (user.current_exercise is None):
        raise ValueError(f"User current storage not found")
    
    exercise = storage_to_exercise(user.current_exercise)
    return user, exercise
