import pytest

from src.application import exercise_selection
from src.application.services import onboarding, placement
from src.domain.enums import (
    Band,
    Direction,
    ExerciseStyle,
    ExerciseTypes,
    LengthPreference,
    OnboardingStep,
    Tenses,
    Topics,
    WeeklyTime,
)
from src.domain.models.exercise import AreasOfFocus
from src.domain.models.profile import PlacementSubmission, UserGoals
from src.infrastructure.llm.contracts.placement import PlacementAssessment

GOALS = UserGoals(
    direction=Direction.TRAVEL,
    desired_band=Band.B1,
    weekly_time=WeeklyTime.T_1_2H,
    length_preference=LengthPreference.STANDARD,
)


def test_new_user_starts_at_the_goals_step(deps, fake_users):
    user = fake_users.seed_new("newbie")
    assert onboarding.current_step(user) is OnboardingStep.GOALS


def test_goals_then_placement_then_ready(deps, fake_users, fake_llm):
    fake_users.seed_new("newbie")

    user = onboarding.save_goals("newbie", GOALS)
    assert onboarding.current_step(user) is OnboardingStep.PLACEMENT
    assert user.proficiency.current is Band.A1

    fake_llm.structured_responses = {
        PlacementAssessment: PlacementAssessment(
            writing_signal=0.55,
            reading_signal=0.66,
            notes_en="You handle the present tense well.",
        ),
    }

    form = placement.build_form()
    answers = {item.id: item.options[0] for item in form.mcq}
    result = placement.submit(
        "newbie",
        PlacementSubmission(
            mcq_answers=answers,
            writing_response="El fin de semana pasado fui al mercado con mi hermana.",
            reading_answers=["En un pueblo cerca del mar.", "Camina a la panaderia.", "Viajar a las montanas."],
        ),
    )

    assert result["assigned_band"] in {band.value for band in Band}
    assert result["mcq_total"] == len(form.mcq)

    placed = fake_users.saved["newbie"]
    assert placed.placement.completed is True
    assert onboarding.current_step(placed) is OnboardingStep.READY
    assert placed.proficiency.current.value == result["assigned_band"]


def test_placement_form_never_leaks_answers(deps):
    form = placement.build_form()
    dumped = form.model_dump_json()
    assert "answer" not in dumped
    assert len(form.mcq) > 0
    assert form.reading_questions


def test_placement_requires_goals_first(deps, fake_users):
    fake_users.seed_new("newbie")
    with pytest.raises(ValueError, match="goals"):
        placement.submit("newbie", PlacementSubmission())


def test_exercises_are_blocked_until_placement(deps, fake_users):
    fake_users.seed_new("newbie")
    onboarding.save_goals("newbie", GOALS)

    with pytest.raises(ValueError, match="placement"):
        exercise_selection.generate_exercise(
            "newbie",
            ExerciseTypes.WRITING,
            ExerciseStyle.PREFERENCES,
            AreasOfFocus(focus_topics=[Topics.TRAVEL]),
        )


def test_empty_placement_submission_places_at_the_floor(deps, fake_users, fake_llm):
    fake_users.seed_new("newbie")
    onboarding.save_goals("newbie", GOALS)

    # No samples, so the service short-circuits and never calls the model.
    result = placement.submit("newbie", PlacementSubmission())

    assert result["assigned_band"] == Band.A1.value
    assert fake_llm.structured_calls == []


def test_band_drives_exercise_difficulty_not_the_client(deps, fake_users):
    fake_users.seed("beginner", band=Band.A1)
    fake_users.seed("intermediate", band=Band.B1)

    easy = exercise_selection.generate_exercise(
        "beginner", ExerciseTypes.WRITING, ExerciseStyle.WEAKNESSES, None
    )
    hard = exercise_selection.generate_exercise(
        "intermediate", ExerciseTypes.WRITING, ExerciseStyle.WEAKNESSES, None
    )

    easy_config = fake_users.saved["beginner"].current_exercise.exercise_config
    hard_config = fake_users.saved["intermediate"].current_exercise.exercise_config

    assert easy.band is Band.A1 and hard.band is Band.B1
    assert easy_config.word_count < hard_config.word_count
    assert easy_config.cefr_hint and hard_config.cefr_hint


def test_weak_areas_stay_within_the_band(deps, fake_users):
    """An A1 learner must never be handed a tense the band has not introduced."""
    fake_users.seed("beginner", band=Band.A1)

    exercise_selection.generate_exercise(
        "beginner", ExerciseTypes.WRITING, ExerciseStyle.WEAKNESSES, None
    )

    focus = fake_users.saved["beginner"].current_exercise.areas_of_focus
    assert focus.focus_tenses == [Tenses.PRESENTE_DE_INDICATIVO]


def test_length_preference_reaches_the_exercise_config(deps, fake_users):
    fake_users.seed("shorty", band=Band.B1, length=LengthPreference.SHORT)
    fake_users.seed("lengthy", band=Band.B1, length=LengthPreference.LONG)

    for name in ("shorty", "lengthy"):
        exercise_selection.generate_exercise(
            name, ExerciseTypes.WRITING, ExerciseStyle.WEAKNESSES, None
        )

    short = fake_users.saved["shorty"].current_exercise.exercise_config
    long_ = fake_users.saved["lengthy"].current_exercise.exercise_config

    assert short.length is LengthPreference.SHORT
    assert short.word_count < long_.word_count


def test_plan_summary_estimates_time_to_target(deps, fake_users):
    user = fake_users.seed("planner", band=Band.A2)
    plan = onboarding.plan_summary(user)

    assert plan["current_band"] == Band.A2.value
    assert plan["target_band"] == Band.B1.value
    assert plan["half_steps_remaining"] == 2
    assert plan["estimated_weeks"] > 0
    assert plan["current_gloss"]
