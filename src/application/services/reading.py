from datetime import datetime
from src.application.exercise_selection import create_exercise_context
from src.domain.models.exercise import ExerciseContext
from src.domain.models.progress import Progress
from src.infrastructure.llm.contracts.reading import ReadingGeneration, QuestionMarking
from src.infrastructure.llm.contracts.shared import AgentNames
from src.infrastructure.llm.prompts.reading import r_answer_system_prompt, r_generation_system_prompt
from src.infrastructure.llm.prompts.writing import w_tagging_system_prompt
from src.infrastructure.llm.harness import agent_inputs, response_format
from src.domain.models.session import Session
from src.infrastructure.persistence.file_storage import save_user_state
from src.infrastructure.persistence.session_storage import store_exercise, update_progress
from src.infrastructure.persistence.user_storage import user_exercise_cache

def reading_mode_run(current_session: Session):
    exercise_context = create_exercise_context(current_session.current_exercise)

    reading_prompt = create_text(exercise_context)
    print(reading_prompt.passage)

    user_responses = []
    for question in reading_prompt.questions:
        user_responses.append(input(f"\nQ. {question}\nAnswer here: "))

    progress = response_tagging(user_responses, reading_prompt, exercise_context)
    
    response_feedback = question_marking(user_responses, reading_prompt, exercise_context)

    for response in response_feedback.individual_questions:
        print(f"A. {response}")
    print(response_feedback.general_feedback)

    exercise_storage = store_exercise(current_session.current_exercise, progress, reading_prompt, user_responses, response_feedback)
                                      
    return exercise_storage

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

    if (user.current_exercise is None) or not isinstance(user.current_exercise.prompt, ReadingGeneration):
        raise ValueError(f"User current storage not found")
    
    exercise_context = create_exercise_context(exercise)

    tags = response_tagging(responses, user.current_exercise.prompt, exercise_context)
    feedback = question_marking(responses, user.current_exercise.prompt, exercise_context)

    user.current_exercise.user_response = responses
    user.current_exercise.feedback = feedback
    user.current_exercise.score = tags
    user.current_exercise.end_time = datetime.now()
    
    finished_exercise = user.current_exercise

    user.exercise_history.append(finished_exercise)
    user.progress_history.append(update_progress(user, finished_exercise))

    save_user_state(user)

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
