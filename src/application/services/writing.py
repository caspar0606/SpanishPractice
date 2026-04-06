from datetime import datetime

from src.application.exercise_selection import create_exercise_context
from src.domain.models.exercise import ExerciseContext
from src.domain.models.progress import Progress
from src.infrastructure.llm.contracts.writing import WritingCorrection, WritingSummary
from src.infrastructure.llm.contracts.shared import AgentInputs, AgentNames
from src.infrastructure.llm.prompts.writing import w_tagging_system_prompt, w_correcting_system_prompt, \
                                                    w_instruction_system_prompt, w_summary_system_prompt
from src.infrastructure.llm.harness import agent_inputs, agent_run, response_format
from src.domain.models.session import Session
from src.infrastructure.persistence.file_storage import save_user_state
from src.infrastructure.persistence.session_storage import store_exercise, update_progress
from src.infrastructure.persistence.user_storage import user_exercise_cache

def writing_mode_run(current_session: Session):
    exercise_context = create_exercise_context(current_session.current_exercise)

    writing_instruction = create_instructions(exercise_context)

    print(f"\nHere is your writing prompt, ¡Buena Suerte! \n\n {writing_instruction}")

    user_response = input("\nPaste/write your response here: ")

    exercise_counts = progress_tagging(user_response, exercise_context)

    corrected_text = text_correction(user_response, exercise_context, writing_instruction)
    print(corrected_text.corrected_version)

    summaries = correction_summary(corrected_text, exercise_context, exercise_counts)
    print(summaries.general_feedback)

    exercise_storage = store_exercise(current_session.current_exercise, exercise_counts, writing_instruction, user_response, summaries)

    return exercise_storage


def generate_instructions(username: str) -> str:
    user, exercise = user_exercise_cache(username)

    if (user.current_exercise is None):
        raise ValueError(f"User current storage not found")
    
    exercise_context = create_exercise_context(exercise)

    prompt = create_instructions(exercise_context)

    user.current_exercise.prompt = prompt
    save_user_state(user)

    return prompt
    
def submit_response(response: str, username: str) -> tuple[WritingCorrection, WritingSummary]:
    user, exercise = user_exercise_cache(username)

    if (user.current_exercise is None) or not (isinstance(user.current_exercise.prompt, str)):
        raise ValueError(f"User current storage not found")

    exercise_context = create_exercise_context(exercise)

    tags = progress_tagging(response, exercise_context)
    corrected = text_correction(response, exercise_context, user.current_exercise.prompt)
    summary = correction_summary(corrected, exercise_context, tags)

    user.current_exercise.user_response = response
    user.current_exercise.feedback = corrected, summary
    user.current_exercise.score = tags
    user.current_exercise.end_time = datetime.now()
    
    finished_exercise = user.current_exercise
    
    user.exercise_history.append(finished_exercise)
    user.progress_history.append(update_progress(user, finished_exercise))
    save_user_state(user)

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

    agent_input = agent_inputs(name=AgentNames.WRITING_TAGGING, system_prompt=w_tagging_system_prompt, 
                               exercise_context=exercise_context, input=user_response, schema=Progress)

    return response_format(agent_input, Progress)

def text_correction(user_response: str, exercise_context: ExerciseContext, writing_instruction: str):

    agent_input = agent_inputs(AgentNames.WRITING_CORRECTOR, system_prompt=w_correcting_system_prompt, 
                               exercise_context=exercise_context, schema=WritingCorrection, stimulus=writing_instruction,input=user_response)

    return response_format(agent_input, WritingCorrection)

def correction_summary(edits: WritingCorrection, exercise_context: ExerciseContext, exercise_counts: Progress):

    agent_input = agent_inputs(name=AgentNames.WRITING_SUMMARY, system_prompt=w_summary_system_prompt,exercise_context=exercise_context,
        schema=WritingSummary, stimulus=[edits.model_dump_json(), exercise_counts.model_dump_json()])

    return response_format(agent_input, WritingSummary)
