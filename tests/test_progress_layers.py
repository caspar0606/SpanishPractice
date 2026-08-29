"""Progress must record three layers and only bank evidence from real attempts."""

from datetime import datetime, timedelta

from src.api.routers.progress import build_overview
from src.application.services import progress as progress_service
from src.domain.enums import (
    Band,
    ExerciseTypes,
    Grammar,
    LengthPreference,
    RelativeLevel,
    Skill,
    Tenses,
    Topics,
)
from src.domain.models.exercise import AreasOfFocus, ExerciseConfig, ExerciseStorage
from src.domain.models.progress import ComputeStats, Progress
from src.domain.rules import proficiency as proficiency_rules


def score(correct: float, total: float) -> Progress:
    return Progress(
        tenses={Tenses.PRESENTE_DE_INDICATIVO: ComputeStats(total_attempts=total, correct_attempts=correct)},
        grammar={Grammar.GENDER_AGREEMENT: ComputeStats(total_attempts=total, correct_attempts=correct)},
        topics={Topics.TRAVEL: ComputeStats(total_attempts=total, correct_attempts=correct)},
    )


def start_exercise(user, exercise_type=ExerciseTypes.WRITING, minutes_ago=5, band=Band.A2):
    user.current_exercise = ExerciseStorage(
        id=f"ex-{len(user.exercise_history)}",
        type=exercise_type,
        areas_of_focus=AreasOfFocus(focus_topics=[Topics.TRAVEL]),
        exercise_config=ExerciseConfig(
            band=band,
            length=LengthPreference.STANDARD,
            word_count=100,
        ),
        start_time=datetime.now() - timedelta(minutes=minutes_ago),
        prompt="Escribe sobre un viaje.",
    )
    return user


def submit(user, response, correct, total, exercise_type=ExerciseTypes.WRITING):
    start_exercise(user, exercise_type=exercise_type)
    return progress_service.save_user_progress(user, response, ["feedback"], score(correct, total))


def submit_answers(user, answers, correct, total, exercise_type=ExerciseTypes.READING):
    """Item-shaped submission, as reading and drills use."""
    start_exercise(user, exercise_type=exercise_type)
    return progress_service.save_user_progress(
        user,
        answers,
        ["feedback"],
        score(correct, total),
        metrics=progress_service.item_metrics(
            user.current_exercise,
            answered=sum(1 for answer in answers if str(answer).strip()),
            total=len(answers),
        ),
    )


def test_accuracy_ignores_the_inflated_totals_from_tagging():
    """Tagging repeats stats across focus areas, so only the ratio is meaningful."""
    assert progress_service.accuracy_of(score(3, 4)) == 0.75
    assert progress_service.accuracy_of(Progress()) is None


def test_a_real_attempt_records_all_three_layers(deps, fake_users):
    user = fake_users.seed("learner", band=Band.A2)
    verdict = submit(user, "palabra " * 60, correct=8, total=10)

    assert verdict.genuine is True
    stored = fake_users.saved["learner"]

    # Layer three: cross-skill concept totals.
    assert stored.progress.tenses[Tenses.PRESENTE_DE_INDICATIVO].total_attempts == 10
    # Layer three again, scoped to the skill.
    writing = stored.skills[Skill.WRITING]
    assert writing.concepts.tenses[Tenses.PRESENTE_DE_INDICATIVO].total_attempts == 10
    # Layer two.
    assert writing.genuine_attempts == 1
    assert writing.rolling_accuracy == 0.8
    # Layer one.
    assert stored.proficiency.genuine_attempts_at_band == 1


def test_a_throwaway_attempt_is_still_marked_but_banks_no_evidence(deps, fake_users):
    user = fake_users.seed("learner", band=Band.A2)
    verdict = submit(user, "no", correct=0, total=4)

    assert verdict.genuine is False
    stored = fake_users.saved["learner"]

    # It is marked, stored, and still visible to the learner.
    assert len(stored.exercise_history) == 1
    assert stored.exercise_history[0].genuine is False
    assert stored.exercise_history[0].score is not None
    assert stored.progress_history[-1].genuine is False
    assert stored.skills[Skill.WRITING].total_attempts == 1

    # But it leaves no mark on the progress tables or the band.
    assert stored.progress.tenses[Tenses.PRESENTE_DE_INDICATIVO].total_attempts == 0
    assert stored.skills[Skill.WRITING].concepts.tenses[Tenses.PRESENTE_DE_INDICATIVO].total_attempts == 0
    assert stored.proficiency.genuine_attempts_at_band == 0
    assert stored.skills[Skill.WRITING].genuine_attempts == 0


def test_throwaway_attempts_do_not_invent_a_weak_spot(deps, fake_users):
    """Junk submissions must not make a topic look weak and skew what we suggest."""
    user = fake_users.seed("learner", band=Band.A2)
    for _ in range(3):
        submit(fake_users.load("learner"), "no", correct=0, total=4)

    stored = fake_users.saved["learner"]
    overview = build_overview(stored, stored.progress)
    assert all(row.practised is False for row in overview.topics)


def test_skills_are_tracked_separately(deps, fake_users):
    user = fake_users.seed("learner", band=Band.A2)

    for _ in range(4):
        user = fake_users.load("learner")
        submit(user, "palabra " * 60, correct=10, total=10)
    for _ in range(4):
        user = fake_users.load("learner")
        submit_answers(user, ["una respuesta"] * 5, correct=2, total=10)

    stored = fake_users.saved["learner"]
    assert stored.skills[Skill.WRITING].relative_level is RelativeLevel.ABOVE
    assert stored.skills[Skill.READING].relative_level is RelativeLevel.BELOW
    assert set(stored.skills) == {Skill.WRITING, Skill.READING}


def test_short_reading_answers_still_count_as_a_real_attempt(deps, fake_users):
    """Comprehension answers are brief, so they must not be judged on length."""
    user = fake_users.seed("learner", band=Band.A2)
    verdict = submit_answers(user, ["su hermana", "fruta", "el vendedor", "el mercado", "hablaron"], 4, 5)

    assert verdict.genuine is True
    assert fake_users.saved["learner"].skills[Skill.READING].genuine_attempts == 1


def test_band_only_moves_after_sustained_genuine_work(deps, fake_users):
    fake_users.seed("learner", band=Band.A2)

    for _ in range(proficiency_rules.PROMOTION_MIN_ATTEMPTS - 1):
        submit(fake_users.load("learner"), "palabra " * 60, correct=10, total=10)
    assert fake_users.saved["learner"].proficiency.current is Band.A2

    submit(fake_users.load("learner"), "palabra " * 60, correct=10, total=10)
    assert fake_users.saved["learner"].proficiency.current is Band.A2_5

    last = fake_users.saved["learner"].progress_history[-1]
    assert last.band_change == proficiency_rules.PROMOTED
    assert last.skill is Skill.WRITING
    assert last.genuine is True


def test_a_weak_skill_does_not_demote_an_otherwise_strong_learner(deps, fake_users):
    """Reading lagging behind is recorded on reading, not on the overall band."""
    fake_users.seed("learner", band=Band.A2)

    for _ in range(5):
        submit(fake_users.load("learner"), "palabra " * 60, correct=9, total=10)
    for _ in range(4):
        submit_answers(fake_users.load("learner"), ["si"] * 5, correct=2, total=10)

    stored = fake_users.saved["learner"]
    assert stored.proficiency.current is Band.A2
    assert stored.skills[Skill.READING].relative_level is RelativeLevel.BELOW
    assert stored.skills[Skill.WRITING].relative_level is RelativeLevel.ABOVE


def test_throwaway_attempts_never_add_up_to_a_promotion(deps, fake_users):
    fake_users.seed("learner", band=Band.A2)

    for _ in range(proficiency_rules.PROMOTION_MIN_ATTEMPTS * 3):
        submit(fake_users.load("learner"), "si", correct=10, total=10)

    assert fake_users.saved["learner"].proficiency.current is Band.A2


def test_history_records_why_each_attempt_counted(deps, fake_users):
    user = fake_users.seed("learner", band=Band.A2)
    submit(user, "palabra " * 60, correct=6, total=10)

    entry = fake_users.saved["learner"].progress_history[-1]
    assert entry.accuracy == 0.6
    assert entry.band is Band.A2
    assert entry.skill is Skill.WRITING


def test_overview_exposes_all_three_layers_with_english_labels(deps, fake_users):
    user = fake_users.seed("learner", band=Band.A2)
    submit(user, "palabra " * 60, correct=8, total=10)

    stored = fake_users.saved["learner"]
    overview = build_overview(stored, stored.progress)

    assert overview.overall.band is Band.A2
    assert overview.overall.gloss
    assert overview.overall.attempts_until_review == proficiency_rules.PROMOTION_MIN_ATTEMPTS - 1

    assert [row.skill for row in overview.skills] == [Skill.WRITING]
    assert overview.skills[0].label == "Writing"
    assert overview.skills[0].relative_label

    # Every tracked concept appears, whether practised or not, in English.
    assert len(overview.tenses) == len(Tenses) - 1
    labels = {row.key: row.label for row in overview.tenses}
    assert labels["presente_de_indicativo"] == "Present tense"
    assert labels["preterito_imperfecto"] == "Past tense (used to / was doing)"
    assert all("_" not in row.label for row in overview.grammar)


def test_overview_sorts_weakest_practised_concepts_first(deps, fake_users):
    user = fake_users.seed("learner", band=Band.A2)
    start_exercise(user)
    weak = Progress(
        tenses={
            Tenses.PRESENTE_DE_INDICATIVO: ComputeStats(total_attempts=10, correct_attempts=9),
            Tenses.FUTURO_SIMPLE: ComputeStats(total_attempts=10, correct_attempts=2),
        },
    )
    progress_service.save_user_progress(user, "palabra " * 60, ["fb"], weak)

    stored = fake_users.saved["learner"]
    overview = build_overview(stored, stored.progress)

    assert overview.tenses[0].key == "futuro_simple"
    assert overview.tenses[1].key == "presente_de_indicativo"
    # Never-practised concepts sit below the practised ones.
    assert overview.tenses[-1].practised is False
