"""The daily plan is a pure function of user state plus the curriculum."""

from datetime import date, datetime

from src.application.services import recommender as service
from src.domain.enums import (
    Band,
    Direction,
    ExerciseTypes,
    Grammar,
    Tenses,
    Topics,
    VocabStatus,
)
from src.domain.models.exercise import AreasOfFocus, ExerciseConfig, ExerciseStorage
from src.domain.models.progress import ComputeStats
from src.domain.models.vocab import VocabEntry
from src.domain.rules import curriculum as curriculum_rules
from src.infrastructure.persistence.json_content import JsonContentRepository


def steps():
    return curriculum_rules.parse_steps(JsonContentRepository().curriculum())


def practise(user, tense=None, grammar=None, correct=2, total=10):
    stats = ComputeStats(total_attempts=total, correct_attempts=correct)
    if tense is not None:
        user.progress.tenses[tense] = stats
    if grammar is not None:
        user.progress.grammar[grammar] = stats
    return user


def finish(user, kind, when=None, genuine=True):
    stamp = when or datetime.now()
    user.exercise_history.append(
        ExerciseStorage(
            id=f"h{len(user.exercise_history)}",
            type=kind,
            areas_of_focus=AreasOfFocus(),
            exercise_config=ExerciseConfig(band=Band.A2, word_count=80),
            start_time=stamp,
            end_time=stamp,
            prompt="p",
            genuine=genuine,
        ),
    )
    return user


def slot(plan, kind):
    return next(item for item in plan.daily if item.type is kind)


def test_a_fresh_a2_learner_gets_four_daily_skills(deps, fake_users):
    user = fake_users.seed("learner", band=Band.A2)
    plan = service.plan_for(user, steps())

    assert [item.type for item in plan.daily] == [
        ExerciseTypes.WRITING,
        ExerciseTypes.READING,
        ExerciseTypes.LISTENING,
        ExerciseTypes.SPEAKING,
    ]
    assert plan.remaining == 4
    assert plan.complete is False
    assert all(not item.done for item in plan.daily)
    assert all(item.reason_en for item in plan.daily)


def test_writing_uses_the_weakest_introduced_concept(deps, fake_users):
    user = fake_users.seed("learner", band=Band.A2)
    practise(user, tense=Tenses.PRESENTE_DE_INDICATIVO, correct=9, total=10)
    practise(user, tense=Tenses.PRETERITO_IMPERFECTO, correct=2, total=10)

    writing = slot(service.plan_for(user, steps()), ExerciseTypes.WRITING)
    assert writing.focus.focus_tenses == [Tenses.PRETERITO_IMPERFECTO]
    assert "past tense (used to / was doing)" in writing.reason_en.lower()


def test_writing_ignores_a_weak_concept_the_band_has_not_unlocked(deps, fake_users):
    user = fake_users.seed("learner", band=Band.A2)
    practise(user, tense=Tenses.PRESENTE_DE_INDICATIVO, correct=8, total=10)
    practise(user, tense=Tenses.FUTURO_SIMPLE, correct=0, total=10)

    writing = slot(service.plan_for(user, steps()), ExerciseTypes.WRITING)
    assert writing.focus.focus_tenses == [Tenses.PRESENTE_DE_INDICATIVO]


def test_reading_uses_the_next_named_concept_on_the_roadmap(deps, fake_users):
    user = fake_users.seed("learner", band=Band.A2)
    reading = slot(service.plan_for(user, steps()), ExerciseTypes.READING)
    assert reading.focus.focus_tenses == [Tenses.FUTURO_SIMPLE]
    assert "future tense" in reading.reason_en.lower()


def test_writing_can_target_a_grammar_point(deps, fake_users):
    user = fake_users.seed("learner", band=Band.A2)
    practise(user, tense=Tenses.PRESENTE_DE_INDICATIVO, correct=9, total=10)
    practise(user, grammar=Grammar.VERB_SUBJECT_CONJUGATION, correct=1, total=10)

    writing = slot(service.plan_for(user, steps()), ExerciseTypes.WRITING)
    assert writing.focus.focus_grammar == [Grammar.VERB_SUBJECT_CONJUGATION]
    assert "matching verbs" in writing.reason_en.lower()


def test_listening_follows_the_learner_direction(deps, fake_users):
    user = fake_users.seed("learner", band=Band.A2)
    user.goals.direction = Direction.SCHOOL
    fake_users.save(user)

    listening = slot(service.plan_for(fake_users.load("learner"), steps()), ExerciseTypes.LISTENING)
    assert listening.focus.focus_topics == [Topics.SCHOOL]
    assert "school" in listening.reason_en.lower()


def test_finishing_writing_today_marks_that_slot_done(deps, fake_users):
    user = fake_users.seed("learner", band=Band.A2)
    today = date(2026, 8, 29)
    finish(user, ExerciseTypes.WRITING, when=datetime(2026, 8, 29, 9, 0))

    plan = service.plan_for(user, steps(), today=today)
    assert slot(plan, ExerciseTypes.WRITING).done is True
    assert slot(plan, ExerciseTypes.READING).done is False
    assert plan.remaining == 3
    assert plan.complete is False


def test_sydney_evening_counts_as_the_learners_next_calendar_day(deps, fake_users):
    """Railway stores naive UTC. Sydney (UTC+10) offset is -600 in JS."""
    user = fake_users.seed("learner", band=Band.A2)
    finish(user, ExerciseTypes.WRITING, when=datetime(2026, 8, 30, 22, 0))
    plan = service.plan_for(
        user, steps(), today=date(2026, 8, 31), tz_offset_minutes=-600,
    )
    assert slot(plan, ExerciseTypes.WRITING).done is True
    assert plan.remaining == 3


def test_yesterdays_writing_does_not_count_as_today(deps, fake_users):
    user = fake_users.seed("learner", band=Band.A2)
    finish(user, ExerciseTypes.WRITING, when=datetime(2026, 8, 28, 21, 0))
    plan = service.plan_for(user, steps(), today=date(2026, 8, 29))
    assert slot(plan, ExerciseTypes.WRITING).done is False
    assert plan.remaining == 4


def test_all_four_done_unlocks_extra_drills(deps, fake_users):
    user = fake_users.seed("learner", band=Band.A2)
    day = datetime(2026, 8, 29, 10, 0)
    for kind in (
        ExerciseTypes.WRITING,
        ExerciseTypes.READING,
        ExerciseTypes.LISTENING,
        ExerciseTypes.SPEAKING,
    ):
        finish(user, kind, when=day)

    plan = service.plan_for(user, steps(), today=date(2026, 8, 29))
    assert plan.complete is True
    assert plan.remaining == 0
    assert plan.extras
    assert plan.extras[0].type is ExerciseTypes.DRILLS


def test_a_b2_learner_still_gets_four_daily_slots(deps, fake_users):
    user = fake_users.seed("learner", band=Band.B2)
    plan = service.plan_for(user, steps())
    assert len(plan.daily) == 4
    reading = slot(plan, ExerciseTypes.READING)
    assert reading.focus.focus_topics == [Topics.TRAVEL]


def test_due_vocab_is_an_extra_not_a_daily_slot(deps, fake_users):
    user = fake_users.seed("learner", band=Band.A2)
    user.vocab = [
        VocabEntry(lemma=f"word{i}", gloss_en=f"gloss {i}", status=VocabStatus.NEW)
        for i in range(5)
    ]
    fake_users.save(user)

    plan = service.plan_for(fake_users.load("learner"), steps())
    assert plan.extras[0].kind.value == "vocab"
    assert len(plan.daily) == 4
    assert plan.remaining == 4


def test_recommend_loads_the_user_and_the_shipped_curriculum(deps, fake_users):
    fake_users.seed("learner", band=Band.A1)
    plan = service.recommend("learner")
    assert len(plan.daily) == 4
    assert slot(plan, ExerciseTypes.WRITING).focus.focus_tenses == [Tenses.PRESENTE_DE_INDICATIVO]
    assert slot(plan, ExerciseTypes.READING).focus.focus_tenses == [Tenses.PRETERITO_PERFECTO_SIMPLE]


def test_recommend_refuses_a_learner_who_has_not_placed(deps, fake_users):
    fake_users.seed("learner", band=Band.A2, placed=False)
    try:
        service.recommend("learner")
    except ValueError as exc:
        assert "placement" in str(exc).lower()
    else:
        raise AssertionError("expected placement to be required")
