from src.application import container
from src.domain.models.exercise import Exercise, ExerciseStorage
from src.domain.models.user import User


def user_from_name(username: str) -> User:
    user = container.users().load(username)

    if user is None:
        raise ValueError(f"User '{username}' not found")

    if user.current_exercise is None:
        raise ValueError(f"User '{username}' has no current exercise")

    return user


def storage_to_exercise(storage: ExerciseStorage) -> Exercise:
    return Exercise(
        id=storage.id,
        exercise_type=storage.type,
        band=storage.exercise_config.band,
        length=storage.exercise_config.length,
        areas_of_focus=storage.areas_of_focus,
        start_time=storage.start_time,
    )


def user_exercise_cache(username: str) -> tuple[User, Exercise]:
    user = user_from_name(username)

    if user.current_exercise is None:
        raise ValueError(f"User '{username}' has no current exercise")

    return user, storage_to_exercise(user.current_exercise)
