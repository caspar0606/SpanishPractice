from datetime import datetime

from src.application.exercise_selection import create_exercise_context
from src.application.services.progress import build_drill_progress_update
from src.domain.enums import DrillTypes
from src.domain.models.exercise import Exercise, ExerciseContext
from src.domain.rules.config import QUESTION_NUMBER_CONFIG
from src.domain.rules.score import combine_scores
from src.infrastructure.llm.contracts.drills import DrillMarkingSet, Drills, MarkedDrills, UserDrillResponses, DrillSet
from src.infrastructure.llm.contracts.shared import AgentNames
from src.infrastructure.llm.prompts.drills import DRILLS_PROMPT_CONFIG
from src.infrastructure.llm.harness import agent_inputs, response_format
from src.domain.models.progress import ComputeStats
from src.infrastructure.persistence.file_storage import save_user_state
from src.infrastructure.persistence.file_storage import save_user_state
from src.infrastructure.persistence.session_storage import update_progress
from src.infrastructure.persistence.user_storage import user_exercise_cache


def drills_mode_run(exercise: Exercise):
    exercise_context = create_exercise_context(exercise)
    exercise_context.exercise_config.word_count = 0

    drills = create_drills(exercise_context)

    user_responses = UserDrillResponses(responses={})

    marked_drills = mark_drill_sets(user_responses, drills, exercise_context)
    
    return marked_drills

def generate_drills(username: str) -> Drills:
    user, exercise = user_exercise_cache(username)

    if user.current_exercise is None:
        raise ValueError(f"User current storage not found")
    
    exercise_context = create_exercise_context(exercise)
    exercise_context.exercise_config.word_count = 0

    drills = create_drills(exercise_context)

    user.current_exercise.prompt = drills
    save_user_state(user)

    return drills

def submit_drills(username: str, responses: UserDrillResponses) -> MarkedDrills:
    user, exercise = user_exercise_cache(username)

    if user.current_exercise is None or user.current_exercise.prompt is None:
        raise ValueError(f"User current storage not found")

    raw = user.current_exercise.prompt
    if isinstance(raw, Drills):
        drills_prompt = raw
    elif isinstance(raw, dict):
        drills_prompt = Drills.model_validate(raw)
        user.current_exercise.prompt = drills_prompt
    else:
        raise ValueError(f"User current storage not found")

    exercise_context = create_exercise_context(exercise)

    feedback = mark_drill_sets(responses, drills_prompt, exercise_context)


    user.current_exercise.user_response = responses

    drill_progress_update = build_drill_progress_update(exercise_context, feedback)
    combine_scores(user.progress, drill_progress_update)


    user.current_exercise.score = drill_progress_update
    user.current_exercise.feedback = feedback
    user.current_exercise.end_time = datetime.now()
    
    finished_exercise = user.current_exercise

    user.exercise_history.append(finished_exercise)
    user.progress_history.append(update_progress(user, finished_exercise))

    save_user_state(user)

    return feedback

def create_drills(exercise_context: ExerciseContext) -> Drills:
    question_set = QUESTION_NUMBER_CONFIG[exercise_context.exercise_config.difficulty]

    return Drills(drill_sets={
                drill_type: generate_drill_set(exercise_context, question_set, drill_type) 
                for drill_type in DrillTypes
                }
            )

def mark_drill_sets(user_responses: UserDrillResponses, drills: Drills, exercise_context: ExerciseContext) -> MarkedDrills:

    corrected_drills = [mark_drill_set(user_responses.responses[drill_type], drills.drill_sets[drill_type], 
                                    exercise_context, drill_type) for drill_type in DrillTypes]
    
    for drill_set in corrected_drills:
        drill_set.stats = ComputeStats(
        total_attempts=len(drill_set.marked_drills),
        correct_attempts=sum(d.is_correct for d in drill_set.marked_drills))

    marked_drills = MarkedDrills(marked_drill_sets=corrected_drills, 
                                 stats=ComputeStats(
                                     total_attempts=sum(drill_set.stats.total_attempts for drill_set in corrected_drills),
                                     correct_attempts=sum(drill_set.stats.correct_attempts for drill_set in corrected_drills)))
    
    return marked_drills



def generate_drill_set(exercise_context: ExerciseContext, question_set: dict, drill_type: DrillTypes) -> DrillSet:

    agent_input = agent_inputs(name=AgentNames.SENTENCE_COMPLETION_GENERATOR, 
                               system_prompt=DRILLS_PROMPT_CONFIG[drill_type]["generate"],
                               exercise_context=exercise_context,
                               schema=DrillSet,
                               stimulus=f"number_of_questions: {question_set[drill_type]}")
    
    return response_format(agent_input, DrillSet)



def mark_drill_set(user_response: list[str], drill_set: DrillSet, exercise_context: ExerciseContext, drill_type: DrillTypes):

    agent_input = agent_inputs(name=AgentNames.SENTENCE_COMPLETION_GENERATOR, 
                               system_prompt=DRILLS_PROMPT_CONFIG[drill_type]["mark"],
                               exercise_context=exercise_context,
                               schema=DrillMarkingSet,
                               input=user_response,
                               stimulus=[drill_set.model_dump_json()])
    
    return response_format(agent_input, DrillMarkingSet)
