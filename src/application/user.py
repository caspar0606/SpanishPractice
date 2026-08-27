import os

from dotenv import load_dotenv

from src.domain.models.user import User
from src.domain.utils import initialise_progress
from src.infrastructure.persistence.file_storage import create_new_user_file, load_user_state, save_user_state

# Creates a new user with initialised progress and name
def create_user(name: str) -> User:
    progress = initialise_progress()
    return User(name=name, progress=progress, first_time=True)


def select_user(username: str, key: str, new: bool) -> User | None:

    load_dotenv()
    access_key = os.getenv("ACCESS_KEY")
    if not (access_key == key):
        return None

    if new:
        user = create_user(username)
        if create_new_user_file(username) == 1:
            raise ValueError("User Already Exists. Pick a different username.")
        save_user_state(user)
        return user
    
    user = load_user_state(username)

    if user is None:
        raise ValueError("User doesn't exist.")

    return user
