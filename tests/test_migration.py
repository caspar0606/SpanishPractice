"""A v1 user file must survive the upgrade with its history intact."""

import copy

from src.domain.enums import Band
from src.domain.models.user import SCHEMA_VERSION, User
from src.infrastructure.persistence.migrations import to_v2

V1_USER = {
    "name": "legacy",
    "first_time": False,
    "progress": {
        "tenses": {
            "tenses": {"total_attempts": 9, "correct_attempts": 3},
            "presente_de_indicativo": {"total_attempts": 10, "correct_attempts": 7},
        },
        "grammar": {"gender_agreement": {"total_attempts": 4, "correct_attempts": 2}},
        "topics": {"travel": {"total_attempts": 5, "correct_attempts": 4}},
    },
    "current_exercise": None,
    "exercise_history": [
        {
            "id": "ex-1",
            "type": "writing",
            "areas_of_focus": {"focus_topics": ["travel"]},
            "exercise_config": {"difficulty": "novice", "word_count": 120},
            "start_time": "2026-01-01T10:00:00",
            "end_time": "2026-01-01T10:20:00",
            "prompt": "Escribe sobre un viaje.",
            "user_response": "Fui a Madrid.",
            "score": {
                "tenses": {"tenses": {"total_attempts": 2, "correct_attempts": 1}},
                "grammar": {},
                "topics": {},
            },
        },
        {
            "id": "ex-2",
            "type": "reading",
            "areas_of_focus": {"focus_topics": ["work"]},
            "exercise_config": {"difficulty": "intermediate", "word_count": 400},
            "start_time": "2026-01-02T10:00:00",
        },
    ],
    "progress_history": [],
}


def test_v1_user_validates_after_migration():
    user = User.model_validate(to_v2(copy.deepcopy(V1_USER)))

    assert user.schema_version == SCHEMA_VERSION
    assert user.name == "legacy"
    assert len(user.exercise_history) == 2


def test_difficulty_becomes_a_band():
    migrated = to_v2(copy.deepcopy(V1_USER))
    configs = [item["exercise_config"] for item in migrated["exercise_history"]]

    assert configs[0]["band"] == Band.A2.value
    assert configs[1]["band"] == Band.B1.value
    assert all("difficulty" not in config for config in configs)
    assert all(config["word_count"] > 0 for config in configs)


def test_proficiency_seeds_from_hardest_practised_level():
    user = User.model_validate(to_v2(copy.deepcopy(V1_USER)))
    assert user.proficiency.current is Band.B1


def test_migration_forces_re_onboarding():
    """v1 users never set goals or sat placement, so they must be asked."""
    user = User.model_validate(to_v2(copy.deepcopy(V1_USER)))
    assert user.goals is None
    assert user.placement.completed is False


def test_sentinel_keys_are_dropped_everywhere():
    migrated = to_v2(copy.deepcopy(V1_USER))
    assert "tenses" not in migrated["progress"]["tenses"]
    assert "tenses" not in migrated["exercise_history"][0]["score"]["tenses"]


def test_history_and_scores_are_preserved():
    user = User.model_validate(to_v2(copy.deepcopy(V1_USER)))
    from src.domain.enums import Tenses

    assert user.progress.tenses[Tenses.PRESENTE_DE_INDICATIVO].total_attempts == 10
    assert user.exercise_history[0].user_response == "Fui a Madrid."


def test_migration_is_idempotent():
    once = to_v2(copy.deepcopy(V1_USER))
    twice = to_v2(copy.deepcopy(once))
    assert once == twice


def test_v2_file_passes_through_unchanged():
    v2 = to_v2(copy.deepcopy(V1_USER))
    band_before = v2["exercise_history"][0]["exercise_config"]["band"]
    again = to_v2(copy.deepcopy(v2))
    assert again["exercise_history"][0]["exercise_config"]["band"] == band_before
