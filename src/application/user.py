import os

from dotenv import load_dotenv

from src.application import container
from src.domain.models.user import User
from src.domain.utils import initialise_progress, validate_username


def create_user(name: str) -> User:
    progress = initialise_progress()
    return User(name=name, progress=progress, first_time=True)


def select_user(username: str, key: str, new: bool) -> User | None:
    username = validate_username(username)

    load_dotenv()
    access_key = os.getenv("ACCESS_KEY")
    if not (access_key == key):
        return None

    users = container.users()

    if new:
        user = create_user(username)
        if not users.create(username):
            raise ValueError("User Already Exists. Pick a different username.")
        users.save(user)
        return user

    user = users.load(username)

    if user is None:
        raise ValueError("User doesn't exist.")

    return user
