"""Choosing the areas an exercise should focus on.

Regression cover for category sentinels reaching the generating agent. Because nothing
ever scored them they sat at zero attempts, which made them the weakest areas, which
meant weak_areas() picked them every time. At beginner difficulty a new user's entire
focus set was the three meaningless labels.
"""

import pytest

from src.application.exercise_selection import weak_areas
from src.application.services.progress import build_drill_progress_update
from src.domain.enums import (
    DifficultyLevels,
    ExerciseTypes,
    Grammar,
    Tenses,
    Topics,
    is_category_sentinel,
)
from src.domain.models.exercise import AreasOfFocus, ExerciseConfig, ExerciseContext
from src.domain.models.progress import ComputeStats
from src.domain.rules.config import DIFFICULTY_CONFIG
from src.domain.utils import initialise_progress
from src.infrastructure.llm.contracts.drills import MarkedDrills
from tests.conftest import make_user

TEXT_EXERCISE_TYPES = [ExerciseTypes.WRITING, ExerciseTypes.READING]


class TestAreasOfFocus:
    def test_a_sentinel_sent_as_a_preference_is_ignored(self):
        """A client may post any valid enum value; a sentinel is not a usable focus."""
        focus = AreasOfFocus(
            focus_tenses=[Tenses.TENSES, Tenses.FUTURO_SIMPLE],
            focus_grammar=[Grammar.GRAMMAR],
            focus_topics=[Topics.TOPICS, Topics.WORK],
        )

        assert focus.focus_tenses == [Tenses.FUTURO_SIMPLE]
        assert focus.focus_grammar == []
        assert focus.focus_topics == [Topics.WORK]

    def test_unset_focus_stays_none(self):
        focus = AreasOfFocus(focus_topics=[Topics.SCHOOL])

        assert focus.focus_tenses is None
        assert focus.focus_grammar is None
        assert focus.focus_topics == [Topics.SCHOOL]

    def test_drill_scoring_survives_a_sentinel_preference(self):
        """Progress holds no sentinel, so one reaching a score lookup would raise."""
        context = ExerciseContext(
            areas_of_focus=AreasOfFocus(focus_tenses=[Tenses.TENSES, Tenses.FUTURO_SIMPLE]),
            exercise_config=ExerciseConfig(
                difficulty=DifficultyLevels.BEGINNER, word_count=0
            ),
        )
        feedback = MarkedDrills(
            marked_drill_sets=[], stats=ComputeStats(total_attempts=4, correct_attempts=3)
        )

        score = build_drill_progress_update(context, feedback)

        assert score.tenses[Tenses.FUTURO_SIMPLE] == ComputeStats(
            total_attempts=4, correct_attempts=3
        )


class TestWeakAreaSelection:
    @pytest.mark.parametrize("difficulty", list(DifficultyLevels))
    @pytest.mark.parametrize("exercise_type", TEXT_EXERCISE_TYPES)
    def test_fresh_user_never_focuses_on_a_sentinel(self, difficulty, exercise_type):
        focus = weak_areas(difficulty, None, exercise_type, make_user())

        selected = [*focus.focus_tenses, *focus.focus_grammar, *focus.focus_topics]
        assert selected, "expected at least one focus area"
        assert not any(is_category_sentinel(area) for area in selected)

    @pytest.mark.parametrize("difficulty", list(DifficultyLevels))
    def test_fresh_user_gets_the_configured_number_of_areas(self, difficulty):
        config = DIFFICULTY_CONFIG[difficulty]

        focus = weak_areas(difficulty, None, ExerciseTypes.WRITING, make_user())

        assert len(focus.focus_tenses) == config.num_tenses
        assert len(focus.focus_grammar) == config.num_grammar
        assert len(focus.focus_topics) == config.num_topics

    def test_weakest_practisable_area_is_chosen(self):
        progress = initialise_progress()
        for tense in progress.tenses:
            progress.tenses[tense] = ComputeStats(total_attempts=10, correct_attempts=10)
        progress.tenses[Tenses.CONDICIONAL_SIMPLE] = ComputeStats(
            total_attempts=10, correct_attempts=1
        )

        focus = weak_areas(
            DifficultyLevels.BEGINNER, None, ExerciseTypes.WRITING, make_user(progress)
        )

        assert focus.focus_tenses == [Tenses.CONDICIONAL_SIMPLE]

    def test_a_healed_legacy_user_still_gets_a_full_focus_set(self):
        """A category that held only a sentinel is rebuilt, so selection has candidates."""
        user = make_user(
            initialise_progress().model_validate(
                {"tenses": {}, "grammar": {"grammar": {}}, "topics": {}}
            )
        )

        focus = weak_areas(
            DifficultyLevels.INTERMEDIATE, None, ExerciseTypes.WRITING, user
        )

        assert len(focus.focus_grammar) == DIFFICULTY_CONFIG[
            DifficultyLevels.INTERMEDIATE
        ].num_grammar

    def test_drills_focus_stays_within_the_requested_category(self):
        preferences = AreasOfFocus(focus_grammar=[Grammar.POR_PARA_USAGE])

        focus = weak_areas(
            DifficultyLevels.NOVICE, preferences, ExerciseTypes.DRILLS, make_user()
        )

        assert focus.focus_tenses is None
        assert focus.focus_topics is None
        assert focus.focus_grammar
        assert not any(is_category_sentinel(area) for area in focus.focus_grammar)

    def test_drills_require_preferences(self):
        with pytest.raises(ValueError):
            weak_areas(DifficultyLevels.NOVICE, None, ExerciseTypes.DRILLS, make_user())
