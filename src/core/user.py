from src.domain.classes import ComputeStats, Progress, User
from src.domain.enums import Grammar, Tenses, Topics
from src.domain.enums import Tenses
from src.core.storage import create_new_user_file, save_user_state, load_user_state
from src.app.score import calculate_score
from src.domain.classes import User, DifficultyLevels
from src.domain.enums import Grammar, Topics, Topics
from src.domain.enums import Tenses
from src.domain.preferences import DIFFICULTY_CONFIG

# Creates a new user with initialised progress and name
def create_user(name: str) -> User:
    progress = Progress(
        tenses={tense: ComputeStats(total_attempts=0, correct_attempts=0) for tense in Tenses},
        grammar={grammar: ComputeStats(total_attempts=0, correct_attempts=0) for grammar in Grammar},
        topics={topic: ComputeStats(total_attempts=0, correct_attempts=0) for topic in Topics}
    )
    return User(name=name, progress=progress, first_time=True)



# Determines user's weakest area based on their progress and selected difficulty level
def weak_areas(difficulty_level: DifficultyLevels, user: User):
    config = DIFFICULTY_CONFIG[difficulty_level]  # type: ignore

    # Sorts tense, grammar, and topic progress by score and selects weakest k areas based on the difficulty config
    sorted_tenses = sorted(
        user.progress.tenses.items(),
        key=lambda item: calculate_score(item[1])
    )

    sorted_grammar = sorted(
        user.progress.grammar.items(),
        key=lambda item: calculate_score(item[1])
    )

    sorted_topics = sorted(
        user.progress.topics.items(),
        key=lambda item: calculate_score(item[1])
    )

    # Returns as lists of Tenses, Grammar, and Topics
    return  [Tenses(tense) for tense, _ in sorted_tenses[:config.num_tenses]], \
            [Grammar(grammar) for grammar, _ in sorted_grammar[:config.num_grammar]], \
            [Topics(topic) for topic, _ in sorted_topics[:config.num_topics]]


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

