
from typing import Tuple

from src.application import container
from src.application.exercise_selection import create_exercise_context
from src.application.services.exercise_common import user_exercise_cache
from src.application.services.progress import save_user_progress
from src.domain.enums import AgentNames
from src.domain.models.exercise import ExerciseContext
from src.domain.models.llm import agent_request
from src.domain.models.progress import Progress
from src.infrastructure.llm.contracts.reading import ReadingGeneration, QuestionMarking, TextCorrections
from src.infrastructure.llm.prompts.reading import r_answer_system_prompt, r_generation_system_prompt, \
                                                    r_text_correction_system_prompt, r_progress_tagging_system_prompt


def generate_passage(username: str) -> ReadingGeneration:
    user, exercise = user_exercise_cache(username)

    if (user.current_exercise is None):
        raise ValueError(f"User current storage not found")
    
    exercise_context = create_exercise_context(exercise)

    prompt = create_text(exercise_context)

    user.current_exercise.prompt = prompt
    container.users().save(user)

    return prompt

def submit_response(responses: list[str], username: str) -> Tuple[TextCorrections, QuestionMarking]:
    user, exercise = user_exercise_cache(username)

    if user.current_exercise is None or user.current_exercise.prompt is None:
        raise ValueError(f"User current storage not found")

    raw = user.current_exercise.prompt
    if isinstance(raw, ReadingGeneration):
        reading_prompt = raw
    elif isinstance(raw, dict):
        reading_prompt = ReadingGeneration.model_validate(raw)
        user.current_exercise.prompt = reading_prompt
    else:
        raise ValueError(f"User current storage not found")

    exercise_context = create_exercise_context(exercise)

    tags = response_tagging(responses, reading_prompt, exercise_context)
    corrections = text_correction(responses, exercise_context, user.current_exercise.prompt)
    feedback = question_marking(responses, reading_prompt, exercise_context)

    save_user_progress(user, responses, [feedback, corrections], tags)

    return corrections, feedback


def create_text(exercise_context: ExerciseContext):

    request = agent_request(AgentNames.READING_GENERATOR, system_prompt=r_generation_system_prompt,
                            exercise_context=exercise_context, schema=ReadingGeneration)

    return container.llm().structured(request, ReadingGeneration)



def response_tagging(user_responses: list[str], reading_prompt: ReadingGeneration, exercise_context: ExerciseContext):

    request = agent_request(AgentNames.READING_TAGGING, system_prompt=r_progress_tagging_system_prompt, exercise_context=exercise_context,
                            input=user_responses, schema=Progress, stimulus=reading_prompt)

    return container.llm().structured(request, Progress)


def text_correction(user_response: list[str], exercise_context: ExerciseContext, writing_instruction: str):

    request = agent_request(AgentNames.READING_CORRECTOR, system_prompt=r_text_correction_system_prompt,
                            exercise_context=exercise_context, schema=TextCorrections, stimulus=writing_instruction, input=user_response)

    return container.llm().structured(request, TextCorrections)


def question_marking(user_responses: list[str], reading_prompt: ReadingGeneration, exercise_context: ExerciseContext):

    request = agent_request(AgentNames.READING_SUMMARY, system_prompt=r_answer_system_prompt, schema=QuestionMarking,
                            exercise_context=exercise_context, stimulus=reading_prompt, input=user_responses)

    return container.llm().structured(request, QuestionMarking)
