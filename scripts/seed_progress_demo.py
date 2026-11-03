"""Seeds a learner with a mixed exercise history so the progress UI has data.

Development helper only. Point USERDATA_DIR at a scratch directory first.
"""

import os
from datetime import datetime, timedelta

os.environ.setdefault("USERDATA_DIR", "/tmp/sp_testdata")

from src.api.main import configure_container
from src.application import container
from src.application.services import progress as progress_service
from src.domain.enums import (
    Band,
    Direction,
    ExerciseTypes,
    Grammar,
    LengthPreference,
    Tenses,
    Topics,
    WeeklyTime,
)
from src.domain.models.exercise import AreasOfFocus, ExerciseConfig, ExerciseStorage
from src.domain.models.profile import PlacementResult, Proficiency, UserGoals
from src.domain.models.progress import ComputeStats, Progress
from src.domain.models.user import User
from src.domain.utils import initialise_progress

USERNAME = "uitest3"


def fresh_user() -> User:
    return User(
        name=USERNAME,
        progress=initialise_progress(),
        first_time=False,
        goals=UserGoals(
            direction=Direction.TRAVEL,
            desired_band=Band.B1,
            weekly_time=WeeklyTime.T_2_3H,
            length_preference=LengthPreference.STANDARD,
        ),
        proficiency=Proficiency(current=Band.A2, updated_at=datetime.now()),
        placement=PlacementResult(
            completed=True,
            mcq_correct=5,
            mcq_total=8,
            assigned_band=Band.A2,
            taken_at=datetime.now(),
        ),
    )


def tagged(correct: float, total: float, tense, grammar, topic) -> Progress:
    stats = ComputeStats(total_attempts=total, correct_attempts=correct)
    return Progress(tenses={tense: stats}, grammar={grammar: stats}, topics={topic: stats})


def run(kind, response, correct, total, tense, grammar, topic, items=None) -> None:
    user = container.users().load(USERNAME)
    user.current_exercise = ExerciseStorage(
        id=f"ex{len(user.exercise_history)}",
        type=kind,
        areas_of_focus=AreasOfFocus(focus_topics=[topic]),
        exercise_config=ExerciseConfig(band=Band.A2, word_count=100),
        start_time=datetime.now() - timedelta(minutes=8),
        prompt="p",
    )
    metrics = None
    if items is not None:
        metrics = progress_service.item_metrics(
            user.current_exercise, answered=items[0], total=items[1],
        )
    progress_service.save_user_progress(
        user, response, ["fb"], tagged(correct, total, tense, grammar, topic), metrics=metrics,
    )


def main() -> None:
    configure_container()
    container.users().save(fresh_user())

    for _ in range(5):  # strong writing
        run(ExerciseTypes.WRITING, "palabra " * 60, 9, 10,
            Tenses.PRESENTE_DE_INDICATIVO, Grammar.GENDER_AGREEMENT, Topics.TRAVEL)

    for _ in range(4):  # weak reading
        run(ExerciseTypes.READING, ["si"] * 5, 2, 10,
            Tenses.PRETERITO_IMPERFECTO, Grammar.POR_PARA_USAGE, Topics.WORK, items=(5, 5))

    for _ in range(3):  # middling drills
        run(ExerciseTypes.DRILLS, ["a"] * 10, 6, 10,
            Tenses.FUTURO_SIMPLE, Grammar.VERB_SUBJECT_CONJUGATION, Topics.SCHOOL, items=(10, 10))

    for _ in range(2):  # throwaway attempts that must leave no trace
        run(ExerciseTypes.WRITING, "no", 0, 4,
            Tenses.PRESENTE_DE_INDICATIVO, Grammar.GENDER_AGREEMENT, Topics.EMOTIONS)

    user = container.users().load(USERNAME)
    print(
        f"band={user.proficiency.current.value} "
        f"evidence={user.proficiency.evidence_score:.3f} "
        f"attempts_at_band={user.proficiency.genuine_attempts_at_band} "
        f"history={len(user.exercise_history)}",
    )
    print("emotions, touched only by junk attempts:", user.progress.topics[Topics.EMOTIONS])
    for skill, entry in user.skills.items():
        print(
            f"  {skill.value}: {entry.relative_level.value} "
            f"acc={entry.rolling_accuracy:.2f} "
            f"genuine={entry.genuine_attempts}/{entry.total_attempts}",
        )


if __name__ == "__main__":
    main()
