"""Exercises the writing loop through the ports, with no network calls."""

from datetime import timedelta

from src.application import exercise_selection
from src.application.services import writing
from src.domain.enums import Band, ExerciseStyle, ExerciseTypes, Grammar, Tenses, Topics
from src.domain.models.exercise import AreasOfFocus
from src.domain.models.progress import ComputeStats, Progress
from src.infrastructure.llm.contracts.text_correction import TextCorrection
from src.infrastructure.llm.contracts.writing import WritingSummary


# Long enough to read as a real attempt at a standard-length task.
FULL_ANSWER = " ".join(["Ayer fui al mercado con mi hermana y compramos mucha fruta."] * 6)


def spend_time_on_exercise(user, minutes=6):
    """Tests submit instantly, so backdate the start to look like real work."""
    user.current_exercise.start_time -= timedelta(minutes=minutes)


def _tags() -> Progress:
    return Progress(
        tenses={Tenses.PRESENTE_DE_INDICATIVO: ComputeStats(total_attempts=4, correct_attempts=3)},
        grammar={Grammar.GENDER_AGREEMENT: ComputeStats(total_attempts=2, correct_attempts=1)},
        topics={Topics.TRAVEL: ComputeStats(total_attempts=1, correct_attempts=1)},
    )


def _correction() -> TextCorrection:
    return TextCorrection(
        corrected_version="Fui al mercado con mi hermana.",
        tense_errors={},
        grammar_errors={},
        topic_errors={},
        typos=[],
        other_mistakes=[],
    )


def _summary() -> WritingSummary:
    return WritingSummary(
        tense_edits="Consistent past tense.",
        grammar_edits="Watch gender agreement.",
        topic_edits="Stayed on topic.",
        general_feedback="Clear writing overall.",
    )


def test_generate_and_submit_writing(deps, fake_users, fake_llm):
    fake_users.seed("tester", band=Band.A2)

    exercise = exercise_selection.generate_exercise(
        "tester",
        ExerciseTypes.WRITING,
        ExerciseStyle.PREFERENCES,
        AreasOfFocus(focus_topics=[Topics.TRAVEL]),
    )
    assert exercise.exercise_type is ExerciseTypes.WRITING
    assert exercise.band is Band.A2

    prompt = writing.generate_instructions("tester")
    assert prompt == fake_llm.text_response
    assert fake_users.saved["tester"].current_exercise.prompt == prompt

    fake_llm.structured_responses = {
        Progress: _tags(),
        TextCorrection: _correction(),
        WritingSummary: _summary(),
    }

    spend_time_on_exercise(fake_users.saved["tester"])
    corrected, summary, verdict = writing.submit_response(FULL_ANSWER, "tester")

    assert corrected.corrected_version == "Fui al mercado con mi hermana."
    assert summary.general_feedback == "Clear writing overall."
    assert verdict.genuine is True

    stored = fake_users.saved["tester"]
    assert len(stored.exercise_history) == 1
    assert len(stored.progress_history) == 1
    assert stored.progress.tenses[Tenses.PRESENTE_DE_INDICATIVO].total_attempts == 4
    assert stored.progress.tenses[Tenses.PRESENTE_DE_INDICATIVO].correct_attempts == 3


def test_a_one_line_answer_is_marked_but_not_banked(deps, fake_users, fake_llm):
    """The learner still gets feedback, but a token effort leaves no trace."""
    fake_users.seed("tester", band=Band.A2)
    exercise_selection.generate_exercise(
        "tester",
        ExerciseTypes.WRITING,
        ExerciseStyle.PREFERENCES,
        AreasOfFocus(focus_topics=[Topics.TRAVEL]),
    )
    writing.generate_instructions("tester")
    fake_llm.structured_responses = {
        Progress: _tags(),
        TextCorrection: _correction(),
        WritingSummary: _summary(),
    }

    _, summary, verdict = writing.submit_response("Fui al mercado con mi hermana.", "tester")

    assert summary.general_feedback == "Clear writing overall."
    assert verdict.genuine is False
    assert verdict.reasons

    stored = fake_users.saved["tester"]
    assert len(stored.exercise_history) == 1
    assert stored.progress.tenses[Tenses.PRESENTE_DE_INDICATIVO].total_attempts == 0


def test_double_submit_is_rejected(deps, fake_users, fake_llm):
    fake_users.seed("tester")
    exercise_selection.generate_exercise(
        "tester",
        ExerciseTypes.WRITING,
        ExerciseStyle.PREFERENCES,
        AreasOfFocus(focus_topics=[Topics.TRAVEL]),
    )
    writing.generate_instructions("tester")
    fake_llm.structured_responses = {
        Progress: _tags(),
        TextCorrection: _correction(),
        WritingSummary: _summary(),
    }
    writing.submit_response("Fui al mercado.", "tester")

    # The stored exercise is now closed, so a replay must not double-count progress.
    try:
        writing.submit_response("Fui al mercado.", "tester")
    except ValueError:
        pass
    else:
        raise AssertionError("expected the second submit to be rejected")

    assert len(fake_users.saved["tester"].exercise_history) == 1
