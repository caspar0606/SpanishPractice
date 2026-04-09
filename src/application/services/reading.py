from src.application.exercise_selection import create_exercise_context
from src.application.services.progress import save_user_progress
from src.domain.models.exercise import ExerciseContext
from src.domain.models.progress import Progress
from src.infrastructure.llm.contracts.reading import ReadingGeneration, QuestionMarking
from src.infrastructure.llm.contracts.shared import AgentNames
from src.infrastructure.llm.prompts.reading import r_answer_system_prompt, r_generation_system_prompt
from src.infrastructure.llm.prompts.writing import w_tagging_system_prompt
from src.infrastructure.llm.harness import agent_inputs, response_format
from src.infrastructure.persistence.file_storage import save_user_state
from src.infrastructure.persistence.user_storage import user_exercise_cache


def generate_passage(username: str) -> ReadingGeneration:
    user, exercise = user_exercise_cache(username)

    if (user.current_exercise is None):
        raise ValueError(f"User current storage not found")
    
    exercise_context = create_exercise_context(exercise)

    prompt = create_text(exercise_context)

    user.current_exercise.prompt = prompt
    save_user_state(user)

    return prompt

def submit_response(responses: list[str], username: str) -> QuestionMarking:
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
    feedback = question_marking(responses, reading_prompt, exercise_context)

    save_user_progress(user, responses, feedback, tags)

    return feedback


def create_text(exercise_context: ExerciseContext):

    agent_input = agent_inputs(AgentNames.READING_GENERATOR, system_prompt=r_generation_system_prompt, 
                               exercise_context=exercise_context, schema=ReadingGeneration)

    return response_format(agent_input, ReadingGeneration)



def response_tagging(user_responses: list[str], reading_prompt: ReadingGeneration, exercise_context: ExerciseContext):

    agent_input = agent_inputs(AgentNames.WRITING_TAGGING, system_prompt=w_tagging_system_prompt, exercise_context=exercise_context,
                               input=user_responses, stimulus=reading_prompt)

    return response_format(agent_input, Progress)



def question_marking(user_responses: list[str], reading_prompt: ReadingGeneration, exercise_context: ExerciseContext):

    agent_input = agent_inputs(AgentNames.READING_MARKING, r_answer_system_prompt, 
                               exercise_context=exercise_context, stimulus=reading_prompt, input=user_responses)

    return response_format(agent_input, QuestionMarking)
