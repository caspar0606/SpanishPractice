from src.domain.enums import Grammar, Tenses, Topics, practice_members
from src.domain.models.progress import ComputeStats, Progress

def initialise_progress():
    return Progress(
        tenses={tense: ComputeStats(total_attempts=0, correct_attempts=0) for tense in practice_members(Tenses)},
        grammar={grammar: ComputeStats(total_attempts=0, correct_attempts=0) for grammar in practice_members(Grammar)},
        topics={topic: ComputeStats(total_attempts=0, correct_attempts=0) for topic in practice_members(Topics)}
    )
