from src.app.score import calculate_score
from src.domain.classes import CurrentSession


def weak_areas(current_session: CurrentSession):
    config = DIFFICULTY_CONFIG[current_session.current_exercise.difficulty_level] # type: ignore

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

    return sorted_tenses[:config.num_tenses], sorted_grammar[:config.num_grammar], sorted_topics[:config.num_topics]

