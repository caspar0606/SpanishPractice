from src.domain.models.progress import ComputeStats, Progress
from src.domain.enums import Grammar, Tenses, Topics
from src.domain.enums import Tenses
from src.infrastructure.persistence.file_storage import create_new_user_file, save_user_state, load_user_state
from src.domain.models.session import User
from src.domain.enums import Grammar, Topics, Topics
from src.domain.enums import Tenses
from dotenv import load_dotenv
import os

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




def initialise_progress():
    return Progress(
        tenses={tense: ComputeStats(total_attempts=0, correct_attempts=0) for tense in Tenses},
        grammar={grammar: ComputeStats(total_attempts=0, correct_attempts=0) for grammar in Grammar},
        topics={topic: ComputeStats(total_attempts=0, correct_attempts=0) for topic in Topics}
    )