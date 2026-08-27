"""Progress is kept total over the practisable areas.

Every real area is present and no category sentinel ever is. Weak-area selection relies
on this: it picks the lowest-scoring entries, so an area missing from the map can never
be chosen, and a sentinel present in it would always win.
"""

import pytest

from src.domain.enums import is_category_sentinel, practice_members
from src.domain.models.progress import ComputeStats, Progress
from src.domain.utils import initialise_progress
from tests.conftest import FOCUS_CATEGORIES


@pytest.mark.parametrize("category, enum_cls", FOCUS_CATEGORIES)
def test_new_progress_tracks_only_practisable_areas(category, enum_cls):
    tracked = getattr(initialise_progress(), category)

    assert set(tracked) == set(practice_members(enum_cls))


@pytest.mark.parametrize("category, enum_cls", FOCUS_CATEGORIES)
def test_legacy_file_loses_its_sentinel_but_keeps_real_scores(category, enum_cls):
    """User files written before the fix carry a sentinel key; it must not survive."""
    stored = initialise_progress().model_dump(mode="json")
    stored[category][category] = {"total_attempts": 4.0, "correct_attempts": 1.0}

    loaded = getattr(Progress.model_validate(stored), category)

    assert set(loaded) == set(practice_members(enum_cls))


@pytest.mark.parametrize("category, enum_cls", FOCUS_CATEGORIES)
def test_a_category_holding_only_a_sentinel_is_rebuilt(category, enum_cls):
    """Dropping the sentinel must not leave the category empty for weak-area selection."""
    stored = {name: {} for name, _ in FOCUS_CATEGORIES}
    stored[category] = {category: {"total_attempts": 9.0, "correct_attempts": 0.0}}

    loaded = getattr(Progress.model_validate(stored), category)

    assert set(loaded) == set(practice_members(enum_cls))
    assert all(stats == ComputeStats() for stats in loaded.values())


def test_real_scores_in_a_legacy_file_are_preserved():
    stored = {
        "tenses": {
            "tenses": {"total_attempts": 9.0, "correct_attempts": 0.0},
            "futuro_simple": {"total_attempts": 2.0, "correct_attempts": 2.0},
        },
        "grammar": {},
        "topics": {},
    }

    loaded = Progress.model_validate(stored)

    assert loaded.tenses["futuro_simple"] == ComputeStats(
        total_attempts=2, correct_attempts=2
    )


def test_partial_scores_from_a_tagging_agent_are_completed():
    tagged = Progress.model_validate(
        {
            "tenses": {"tenses": {"total_attempts": 2, "correct_attempts": 1}},
            "grammar": {},
            "topics": {"travel": {"total_attempts": 2, "correct_attempts": 2}},
        }
    )

    assert not any(is_category_sentinel(area) for area in tagged.tenses)
    assert tagged.topics["travel"] == ComputeStats(total_attempts=2, correct_attempts=2)
    assert tagged.topics["work"] == ComputeStats()
