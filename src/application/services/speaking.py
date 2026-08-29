"""Speaking mini-exercises: short prompt, Whisper transcript, grammar-only mark."""

from src.application import container
from src.application.exercise_selection import create_exercise_context
from src.application.services import vocab as vocab_file
from src.application.services.exercise_common import user_exercise_cache
from src.application.services.progress import save_user_progress
from src.application.services.writing import correction_summary, progress_tagging
from src.domain.enums import AgentNames
from src.domain.models.exercise import GenuineVerdict
from src.domain.models.llm import agent_request
from src.infrastructure.llm.contracts.text_correction import TextCorrection
from src.infrastructure.llm.contracts.writing import WritingSummary
from src.infrastructure.llm.prompts.speaking import SPEAKING_PROMPT_CONFIG


def generate_prompt(username: str) -> str:
    user, exercise = user_exercise_cache(username)
    if user.current_exercise is None:
        raise ValueError("User current storage not found")

    exercise_context = create_exercise_context(exercise)
    prompt = container.llm().text(
        agent_request(
            name=AgentNames.SPEAKING_INSTRUCTIONS,
            system_prompt=SPEAKING_PROMPT_CONFIG[AgentNames.SPEAKING_INSTRUCTIONS],
            exercise_context=exercise_context,
        ),
    )
    user.current_exercise.prompt = prompt
    container.users().save(user)
    return prompt


def transcribe(username: str, audio_bytes: bytes, filename: str = "speech.webm") -> str:
    user = container.users().load(username)
    if user is None:
        raise ValueError(f"User '{username}' not found")
    if user.current_exercise is None:
        raise ValueError("Start a speaking exercise first")
    return container.stt().transcribe(audio_bytes, filename)


def submit_response(
    username: str,
    transcript: str,
) -> tuple[TextCorrection, WritingSummary, GenuineVerdict]:
    user, exercise = user_exercise_cache(username)
    if user.current_exercise is None or not isinstance(user.current_exercise.prompt, str):
        raise ValueError("User current storage not found")

    exercise_context = create_exercise_context(exercise)
    tags = progress_tagging(transcript, exercise_context)
    corrected = container.llm().structured(
        agent_request(
            AgentNames.SPEAKING_CORRECTOR,
            system_prompt=SPEAKING_PROMPT_CONFIG[AgentNames.SPEAKING_CORRECTOR],
            exercise_context=exercise_context,
            schema=TextCorrection,
            stimulus=user.current_exercise.prompt,
            input=transcript,
        ),
        TextCorrection,
    )
    summary = correction_summary(corrected, exercise_context, tags)
    verdict = save_user_progress(user, transcript, [corrected, summary], tags)
    if verdict.genuine:
        vocab_file.harvest(username, transcript)
    return corrected, summary, verdict
