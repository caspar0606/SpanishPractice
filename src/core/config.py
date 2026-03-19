from src.app.score import calculate_score
from src.domain.classes import CurrentSession
from src.domain.enums import Grammar, Topics, Topics
from src.domain.enums import Tenses
from src.domain.preferences import DIFFICULTY_CONFIG


# Determines user's weakest area based on their progress and selected difficulty level
def weak_areas(current_session: CurrentSession):
    config = DIFFICULTY_CONFIG[current_session.current_exercise.difficulty_level]  # type: ignore

    # Sorts tense, grammar, and topic progress by score and selects weakest k areas based on the difficulty config
    sorted_tenses = sorted(
        current_session.user.progress.tenses.items(),
        key=lambda item: calculate_score(item[1])
    )

    sorted_grammar = sorted(
        current_session.user.progress.grammar.items(),
        key=lambda item: calculate_score(item[1])
    )

    sorted_topics = sorted(
        current_session.user.progress.topics.items(),
        key=lambda item: calculate_score(item[1])
    )

    # Returns as lists of Tenses, Grammar, and Topics
    return  [Tenses(tense) for tense, _ in sorted_tenses[:config.num_tenses]], \
            [Grammar(grammar) for grammar, _ in sorted_grammar[:config.num_grammar]], \
            [Topics(topic) for topic, _ in sorted_topics[:config.num_topics]]

def print_big_lines():
    print("\n" + "-"*50 + "\n")

def print_small_lines():
    print("\n" + "-"*20 + "\n")
