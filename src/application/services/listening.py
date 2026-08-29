"""Listening mini-exercises: a short dialogue, TTS, then comprehension."""

from src.application import container
from src.application.exercise_selection import create_exercise_context
from src.application.services import vocab as vocab_file
from src.application.services.exercise_common import user_exercise_cache
from src.application.services.progress import item_metrics, save_user_progress
from src.domain.enums import AgentNames
from src.domain.models.exercise import GenuineVerdict
from src.domain.models.llm import agent_request
from src.domain.models.progress import Progress
from src.infrastructure.llm.contracts.listening import ListeningGeneration
from src.infrastructure.llm.contracts.reading import QuestionMarking
from src.infrastructure.llm.prompts.listening import LISTENING_PROMPT_CONFIG
from src.infrastructure.llm.prompts.reading import r_answer_system_prompt, r_progress_tagging_system_prompt


def generate_clip(username: str) -> dict:
    user, exercise = user_exercise_cache(username)
    if user.current_exercise is None:
        raise ValueError("User current storage not found")

    exercise_context = create_exercise_context(exercise)
    request = agent_request(
        name=AgentNames.LISTENING_GENERATOR,
        system_prompt=LISTENING_PROMPT_CONFIG[AgentNames.LISTENING_GENERATOR],
        exercise_context=exercise_context,
        schema=ListeningGeneration,
    )
    prompt = container.llm().structured(request, ListeningGeneration)
    spoken = " ".join(turn.line for turn in prompt.dialogue)
    clip_id = container.tts().synthesise(spoken)

    user.current_exercise.prompt = {
        "dialogue": [turn.model_dump() for turn in prompt.dialogue],
        "questions": list(prompt.questions),
        "clip_id": clip_id,
    }
    container.users().save(user)

    return {
        "clip_id": clip_id,
        "audio_url": f"/audio/{clip_id}",
        "questions": list(prompt.questions),
        "turn_count": len(prompt.dialogue),
    }


def load_prompt(raw) -> ListeningGeneration:
    if isinstance(raw, ListeningGeneration):
        return raw
    if isinstance(raw, dict):
        return ListeningGeneration(
            dialogue=raw.get("dialogue") or [],
            questions=raw.get("questions") or [],
        )
    raise ValueError("User current storage not found")


def submit_response(username: str, answers: list[str]) -> tuple[QuestionMarking, GenuineVerdict, str]:
    user, exercise = user_exercise_cache(username)
    if user.current_exercise is None or user.current_exercise.prompt is None:
        raise ValueError("User current storage not found")

    stored = user.current_exercise.prompt
    prompt = load_prompt(stored)
    transcript = "\n".join(f"{turn.speaker}: {turn.line}" for turn in prompt.dialogue)
    exercise_context = create_exercise_context(exercise)

    tags = container.llm().structured(
        agent_request(
            name=AgentNames.READING_TAGGING,
            system_prompt=r_progress_tagging_system_prompt,
            exercise_context=exercise_context,
            input=answers,
            schema=Progress,
            stimulus=prompt,
        ),
        Progress,
    )
    feedback = container.llm().structured(
        agent_request(
            name=AgentNames.READING_SUMMARY,
            system_prompt=r_answer_system_prompt,
            schema=QuestionMarking,
            exercise_context=exercise_context,
            stimulus=prompt,
            input=answers,
        ),
        QuestionMarking,
    )
    verdict = save_user_progress(
        user,
        answers,
        [feedback],
        tags,
        metrics=item_metrics(
            user.current_exercise,
            answered=sum(1 for answer in answers if str(answer).strip()),
            total=len(prompt.questions),
        ),
    )
    if verdict.genuine:
        vocab_file.harvest(username, transcript)
    return feedback, verdict, transcript
