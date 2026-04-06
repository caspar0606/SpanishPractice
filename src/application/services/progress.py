from src.domain.rules.score import add_scores
from src.domain.utils import initialise_progress
from src.infrastructure.persistence.file_storage import load_user_state

def return_progress(username: str):
    user = load_user_state(username)

    if user is None:
        raise ValueError()
    
    return user.progress


def build_drill_progress_update(exercise_context, feedback):
    prog = initialise_progress()
    stats = feedback.stats
    aofs = exercise_context.areas_of_focus

    if aofs.focus_tenses:
        for tense in aofs.focus_tenses:
            if tense is not None:
                add_scores(prog.tenses[tense], stats)

    if aofs.focus_topics:
        for topic in aofs.focus_topics:
            if topic is not None:
                add_scores(prog.topics[topic], stats)

    if aofs.focus_grammar:
        for grammar in aofs.focus_grammar:
            if grammar is not None:
                add_scores(prog.grammar[grammar], stats)

    return prog