from src.domain.models.progress import ComputeStats, Progress
from src.domain.enums import Grammar, Tenses, Topics
from src.domain.enums import Tenses
from src.infrastructure.persistence.file_storage import create_new_user_file, save_user_state, load_user_state
from src.domain.models.session import User
from src.domain.enums import Grammar, Topics, Topics
from src.domain.enums import Tenses

# Creates a new user with initialised progress and name
def create_user(name: str) -> User:
    progress = initialise_progress()
    return User(name=name, progress=progress, first_time=True)



def user_selection():
    while True:
        response = input("Are you a new user (yes/no)?: ").strip().lower()

        if response == "yes": # Creates a new user and saves it as a json file in the userdata directory
            user = create_user(input("Enter your new username: ").strip().lower())
            if create_new_user_file(user.name) == 1: # Checks if User already exists
                continue

            save_user_state(user)
            return user
        
        elif response == "no": # Loads user data
            user = load_user_state(input("Welcome back! Please enter your username: ").strip().lower())

            if user == None: # Checks if User exists
                continue
            return user
        
        else:
            print("Invalid input. Please enter 'yes' or 'no'.")


def initialise_progress():
    return Progress(
        tenses={tense: ComputeStats(total_attempts=0, correct_attempts=0) for tense in Tenses},
        grammar={grammar: ComputeStats(total_attempts=0, correct_attempts=0) for grammar in Grammar},
        topics={topic: ComputeStats(total_attempts=0, correct_attempts=0) for topic in Topics}
    )