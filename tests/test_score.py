"""Folding an exercise's scores into a user's running progress."""

from src.domain.enums import Tenses, Topics
from src.domain.models.progress import ComputeStats, Progress
from src.domain.rules.score import add_scores, calculate_score, combine_scores
from src.domain.utils import initialise_progress


class TestCalculateScore:
    def test_unattempted_area_scores_zero(self):
        assert calculate_score(ComputeStats()) == 0

    def test_score_is_a_percentage(self):
        assert calculate_score(ComputeStats(total_attempts=4, correct_attempts=3)) == 75


class TestAddScores:
    def test_totals_accumulate_in_place(self):
        running = ComputeStats(total_attempts=2, correct_attempts=1)

        add_scores(running, ComputeStats(total_attempts=3, correct_attempts=3))

        assert running == ComputeStats(total_attempts=5, correct_attempts=4)


class TestCombineScores:
    def test_partial_exercise_scores_are_folded_in(self):
        """A marking agent only reports the areas it saw, so its dicts are partial."""
        progress = initialise_progress()
        exercise = Progress(
            tenses={Tenses.FUTURO_SIMPLE: ComputeStats(total_attempts=3, correct_attempts=2)},
            grammar={},
            topics={},
        )

        combine_scores(progress, exercise)

        assert progress.tenses[Tenses.FUTURO_SIMPLE] == ComputeStats(
            total_attempts=3, correct_attempts=2
        )

    def test_areas_absent_from_the_exercise_are_left_alone(self):
        progress = initialise_progress()
        progress.topics[Topics.TRAVEL] = ComputeStats(total_attempts=5, correct_attempts=4)

        combine_scores(progress, Progress(tenses={}, grammar={}, topics={}))

        assert progress.topics[Topics.TRAVEL] == ComputeStats(
            total_attempts=5, correct_attempts=4
        )

    def test_scores_accumulate_across_exercises(self):
        progress = initialise_progress()
        exercise = Progress(
            tenses={},
            grammar={},
            topics={Topics.WORK: ComputeStats(total_attempts=2, correct_attempts=1)},
        )

        combine_scores(progress, exercise)
        combine_scores(progress, exercise)

        assert progress.topics[Topics.WORK] == ComputeStats(
            total_attempts=4, correct_attempts=2
        )

    def test_an_area_missing_from_progress_is_created(self):
        progress = Progress(tenses={}, grammar={}, topics={})
        exercise = Progress(
            tenses={
                Tenses.PRETERITO_IMPERFECTO: ComputeStats(total_attempts=1, correct_attempts=0)
            },
            grammar={},
            topics={},
        )

        combine_scores(progress, exercise)

        assert progress.tenses[Tenses.PRETERITO_IMPERFECTO].total_attempts == 1
