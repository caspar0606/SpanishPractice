"""Shared fixtures and helpers for the domain test suite.

Nothing here touches the LLM harness, so the whole suite runs offline.
"""

from src.domain.enums import Grammar, Tenses, Topics
from src.domain.models.progress import Progress
from src.domain.models.user import User
from src.domain.utils import initialise_progress

# (attribute name on Progress / AreasOfFocus, matching focus enum)
FOCUS_CATEGORIES = [("tenses", Tenses), ("grammar", Grammar), ("topics", Topics)]


def make_user(progress: Progress | None = None) -> User:
    return User(name="tester", progress=progress or initialise_progress(), first_time=True)
