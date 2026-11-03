import re

from src.domain.enums import Grammar, Tenses, Topics, tracked_members
from src.domain.models.progress import ComputeStats, Progress

_USERNAME_RE = re.compile(r"^[A-Za-z0-9._-]{1,64}$")


def validate_username(username: str) -> str:
    name = username.strip()
    if not _USERNAME_RE.fullmatch(name):
        raise ValueError(
            "Username must be 1–64 letters, numbers, dots, underscores, or hyphens."
        )
    return name


def initialise_progress():
    return Progress(
        tenses={tense: ComputeStats(total_attempts=0, correct_attempts=0) for tense in tracked_members(Tenses)},
        grammar={grammar: ComputeStats(total_attempts=0, correct_attempts=0) for grammar in tracked_members(Grammar)},
        topics={topic: ComputeStats(total_attempts=0, correct_attempts=0) for topic in tracked_members(Topics)}
    )
    return Progress(
        tenses={tense: ComputeStats(total_attempts=0, correct_attempts=0) for tense in tracked_members(Tenses)},
        grammar={grammar: ComputeStats(total_attempts=0, correct_attempts=0) for grammar in tracked_members(Grammar)},
        topics={topic: ComputeStats(total_attempts=0, correct_attempts=0) for topic in tracked_members(Topics)}
    )