from src.domain.classes import ComputeStats, Progress, User
from src.domain.enums import Grammar, Tenses, Topics
from src.domain.enums import Tenses

# Creates a new user with initialised progress and name
def create_user(name: str) -> User:
    progress = Progress(
        tenses={tense: ComputeStats(total_attempts=0, correct_attempts=0) for tense in Tenses},
        grammar={grammar: ComputeStats(total_attempts=0, correct_attempts=0) for grammar in Grammar},
        topics={topic: ComputeStats(total_attempts=0, correct_attempts=0) for topic in Topics}
    )
    return User(name=name, progress=progress, first_time=True)