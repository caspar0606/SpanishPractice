"""Listening generate uses TTS; speaking transcribe uses STT."""

from src.application.exercise_selection import generate_exercise
from src.application.services import listening as listening_file
from src.application.services import speaking as speaking_file
from src.domain.enums import ExerciseStyle, ExerciseTypes
from src.infrastructure.llm.contracts.listening import DialogueTurn, ListeningGeneration
from src.infrastructure.llm.contracts.reading import QuestionMarking
from src.domain.models.progress import Progress
from src.domain.utils import initialise_progress


def test_listening_generate_asks_tts_and_hides_transcript(deps, fake_users, fake_llm, fake_tts):
    fake_users.seed("learner")
    generate_exercise("learner", ExerciseTypes.LISTENING, ExerciseStyle.WEAKNESSES, None)
    fake_llm.structured_responses[ListeningGeneration] = ListeningGeneration(
        dialogue=[
            DialogueTurn(speaker="Ana", line="Hola, ¿vas al mercado?"),
            DialogueTurn(speaker="Luis", line="Sí, necesito pan."),
            DialogueTurn(speaker="Ana", line="Vale, vamos juntos."),
        ],
        questions=["¿Adónde va Luis?", "¿Van juntos?"],
    )

    result = listening_file.generate_clip("learner")

    assert result["clip_id"] == "test-clip"
    assert result["audio_url"] == "/audio/test-clip"
    assert "transcript" not in result
    assert fake_tts.calls
    stored = fake_users.saved["learner"].current_exercise.prompt
    assert "clip_id" in stored
    assert stored["questions"][0].startswith("¿")


def test_listening_submit_reveals_transcript(deps, fake_users, fake_llm, fake_tts):
    fake_users.seed("learner")
    generate_exercise("learner", ExerciseTypes.LISTENING, ExerciseStyle.WEAKNESSES, None)
    fake_llm.structured_responses[ListeningGeneration] = ListeningGeneration(
        dialogue=[
            DialogueTurn(speaker="Ana", line="Hola."),
            DialogueTurn(speaker="Luis", line="Hola, Ana."),
            DialogueTurn(speaker="Ana", line="¿Café?"),
        ],
        questions=["¿Se saludan?", "¿Quieren café?"],
    )
    listening_file.generate_clip("learner")
    fake_llm.structured_responses[Progress] = initialise_progress()
    fake_llm.structured_responses[QuestionMarking] = QuestionMarking(
        individual_questions=["Correct."],
        general_feedback="You caught the greeting.",
    )

    feedback, verdict, transcript = listening_file.submit_response("learner", ["Sí"])
    assert "Ana:" in transcript
    assert feedback.general_feedback
    assert verdict is not None


def test_speaking_transcribe_uses_stt(deps, fake_users, fake_stt):
    fake_users.seed("learner")
    generate_exercise("learner", ExerciseTypes.SPEAKING, ExerciseStyle.WEAKNESSES, None)
    text = speaking_file.transcribe("learner", b"fake-bytes")
    assert text == "Hola, estoy bien."
    assert fake_stt.calls
