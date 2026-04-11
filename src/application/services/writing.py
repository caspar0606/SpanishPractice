from src.application.exercise_selection import create_exercise_context
from src.application.services.progress import save_user_progress
from src.domain.models.exercise import ExerciseContext
from src.domain.models.progress import Progress
from src.infrastructure.llm.contracts.writing import WritingSummary
from src.infrastructure.llm.contracts.shared import TextCorrection
from src.infrastructure.llm.contracts.shared import AgentInputs, AgentNames
from src.infrastructure.llm.prompts.writing import w_progress_tagging_system_prompt, w_text_correction_system_prompt, \
                                                    w_instruction_system_prompt, w_summary_system_prompt
from src.infrastructure.llm.harness import agent_inputs, agent_run, response_format
from src.infrastructure.persistence.file_storage import save_user_state
from src.infrastructure.persistence.user_storage import user_exercise_cache


def generate_instructions(username: str) -> str:
    user, exercise = user_exercise_cache(username)

    if (user.current_exercise is None):
        raise ValueError(f"User current storage not found")
    
    exercise_context = create_exercise_context(exercise)

    prompt = create_instructions(exercise_context)

    user.current_exercise.prompt = prompt
    save_user_state(user)

    return prompt
    
def submit_response(response: str, username: str) -> tuple[TextCorrection, WritingSummary]:
    user, exercise = user_exercise_cache(username)

    if (user.current_exercise is None) or not (isinstance(user.current_exercise.prompt, str)):
        raise ValueError(f"User current storage not found")

    exercise_context = create_exercise_context(exercise)

    tags = progress_tagging(response, exercise_context)
    corrected = text_correction(response, exercise_context, user.current_exercise.prompt)
    summary = correction_summary(corrected, exercise_context, tags)

    save_user_progress(user, response, [corrected, summary], tags)

    return corrected, summary


    
def create_instructions(exercise_context: ExerciseContext):    

    agent_input = AgentInputs(
        name=AgentNames.WRITING_INSTRUCTIONS,
        system_prompt=w_instruction_system_prompt,
        exercise_context=exercise_context
    )

    response = agent_run(agent_input)
    return response["messages"][-1].content

def progress_tagging(user_response: str, exercise_context: ExerciseContext):

    agent_input = agent_inputs(name=AgentNames.WRITING_TAGGING, system_prompt=w_progress_tagging_system_prompt, 
                               exercise_context=exercise_context, input=user_response, schema=Progress)

    return response_format(agent_input, Progress)

def text_correction(user_response: str, exercise_context: ExerciseContext, writing_instruction: str):

    agent_input = agent_inputs(AgentNames.WRITING_CORRECTOR, system_prompt=w_text_correction_system_prompt, 
                               exercise_context=exercise_context, schema=TextCorrection, stimulus=writing_instruction,input=user_response)

    return response_format(agent_input, TextCorrection)

def correction_summary(edits: TextCorrection, exercise_context: ExerciseContext, exercise_counts: Progress):

    agent_input = agent_inputs(name=AgentNames.WRITING_SUMMARY, system_prompt=w_summary_system_prompt,exercise_context=exercise_context,
        schema=WritingSummary, stimulus=[edits.model_dump_json(), exercise_counts.model_dump_json()])

    return response_format(agent_input, WritingSummary)
