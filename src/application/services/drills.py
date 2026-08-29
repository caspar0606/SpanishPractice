from src.application import container
from src.application.exercise_selection import create_exercise_context
from src.application.services.exercise_common import user_exercise_cache
from src.application.services.progress import (
    build_drill_progress_update,
    item_metrics,
    save_user_progress,
)
from src.domain.enums import DrillTypes
from src.domain.models.exercise import ExerciseContext, GenuineVerdict
from src.domain.models.llm import agent_request
from src.domain.rules.config import QUESTION_NUMBER_CONFIG
from src.infrastructure.llm.contracts.drills import DrillMarkingSet, Drills, MarkedDrills, UserDrillResponses, DrillSet, \
                                                    DRILL_GENERATE_TYPE_CONFIG, DRILL_MARKING_TYPE_CONFIG
from src.infrastructure.llm.prompts.drills import DRILLS_PROMPT_CONFIG
from src.domain.models.progress import ComputeStats


def generate_drills(username: str) -> Drills:
    """Generates all drill_sets for the exercise, saves drills to user's current session,
    and saves user state.
    
    Args: 
        username: Used to load user and current exercise objects.
        
    Returns:
        All drills for the exercise.
    """
        
    
    user, exercise = user_exercise_cache(username)

    if user.current_exercise is None:
        raise ValueError(f"User current storage not found")
    
    exercise_context = create_exercise_context(exercise)
    exercise_context.exercise_config.word_count = 0

    drills = create_drills(exercise_context)

    user.current_exercise.prompt = drills
    container.users().save(user)

    return drills



def submit_drills(
    username: str,
    responses: UserDrillResponses,
) -> tuple[MarkedDrills, GenuineVerdict]:
    """Marks user responses to drill exercises, updates user progress, and returns LLM feedback.

    Args:
        username: Used to load user and current exercise objects.
        responses: Formatted user responses to drill exercises.


    Returns:
        Feedback including all marked drills, correct answers, user responses, and
        comments, plus whether the attempt counted towards the learner's level.
    """
    
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
    score = build_drill_progress_update(exercise_context, feedback)

    verdict = save_user_progress(
        user,
        responses,
        feedback,
        score,
        metrics=item_metrics(
            user.current_exercise,
            answered=count_answered(responses),
            total=count_questions(drills_prompt),
        ),
    )

    return feedback, verdict


def count_questions(drills: Drills) -> int:
    return sum(len(drill_set.drills or []) for drill_set in drills.drill_sets.values())


def count_answered(responses: UserDrillResponses) -> int:
    """Blank answers are skips, so they do not count as attempted."""
    return sum(
        1
        for answers in responses.responses.values()
        for answer in (answers or [])
        if str(answer).strip()
    )



def create_drills(exercise_context: ExerciseContext) -> Drills:
    """Creates all drills for the exercise, drill are effected by the exercise focuses.
    
    Args: 
        exercise_context: object containing exercise focuses and difficulty.
    
    Returns:
        Drills object containing all drills for the exercise.
    """
    
    #Defines number of questions per drill type
    question_set = QUESTION_NUMBER_CONFIG[exercise_context.exercise_config.band]

    if exercise_context.areas_of_focus.focus_grammar:
        types = [DrillTypes.OPTION_SELECTION, DrillTypes.TRANSLATION, DrillTypes.ERROR_CORRECTION]
        
        return Drills(drill_sets={
            drill_type: create_drill_set(exercise_context, question_set, drill_type) 
            for drill_type in types
            }
        )

    return Drills(drill_sets={
                drill_type: create_drill_set(exercise_context, question_set, drill_type) 
                for drill_type in DrillTypes
                }
            )


def _empty_marking_set(drill_type: DrillTypes) -> DrillMarkingSet:
    """Initialises an empty marking set with specified drill type.
    
    Args: 
        drill_type: from DrillTypes.
    
    Returns:
        empty DrillMarkingSet object with specified drill type.
    """
    
    return DrillMarkingSet(
        drill_type=drill_type,
        marked_drills=[],
        stats=ComputeStats(total_attempts=0, correct_attempts=0),
    )

def mark_drill_sets(user_responses: UserDrillResponses, drills: Drills, exercise_context: ExerciseContext) -> MarkedDrills:
    """Marks each drill attempt from the user's responses using mark_drill_set, then computes 
    the scores based on is_correct flag from each marked drill attempt.
    
    Args: 
        user_responses: Formatted user responses to drill exercises.
        drills: Formatted drills from the exercise.
        exercise_context: object containing exercise focuses and difficulty.
    
    Returns:
        Marked drills including correct answers, user responses, comments, and overall scores.
    """
    
    corrected_drills: list[DrillMarkingSet] = []

    for drill_type in drills.drill_sets:
        drill_set = drills.drill_sets[drill_type]
        answers = user_responses.responses.get(drill_type)
        if answers is None:
            answers = []
        if not drill_set.drills:
            corrected_drills.append(_empty_marking_set(drill_type))
            continue
        if len(answers) != len(drill_set.drills):
            raise ValueError(
                f"Drill type {drill_type.value}: expected {len(drill_set.drills)} answer(s), got {len(answers)}",
            )
        corrected_drills.append(
            mark_drill_set(answers, drill_set, exercise_context, drill_type),
        )
    
    for drill_set in corrected_drills:
        drill_set.stats = ComputeStats(
        total_attempts=len(drill_set.marked_drills),
        correct_attempts=sum(d.is_correct for d in drill_set.marked_drills))

    marked_drills = MarkedDrills(marked_drill_sets=corrected_drills, 
                                 stats=ComputeStats(
                                     total_attempts=sum(drill_set.stats.total_attempts for drill_set in corrected_drills),
                                     correct_attempts=sum(drill_set.stats.correct_attempts for drill_set in corrected_drills)))
    
    return marked_drills



def create_drill_set(exercise_context: ExerciseContext, question_set: dict, drill_type: DrillTypes) -> DrillSet:
    """Creates a drill set based on specified type.
    
    Args: 
        exercise_context: object containing exercise focuses and difficulty.
        question_set: Config object that specifies the number of questions per drill type.
        drill_type: Enum value specifying the type of drill.
    
    Returns:
        A DrillSet object including drill question, correct answer, and [options].
    """
    
    request = agent_request(name=DRILL_GENERATE_TYPE_CONFIG[drill_type],
                            system_prompt=DRILLS_PROMPT_CONFIG[drill_type]["generate"],
                            exercise_context=exercise_context,
                            schema=DrillSet,
                            stimulus=f"number_of_questions: {question_set[drill_type]}")

    result = container.llm().structured(request, DrillSet)
    return result.model_copy(update={"drill_type": drill_type})
            


def mark_drill_set(user_response: list[str], drill_set: DrillSet, 
                   exercise_context: ExerciseContext, drill_type: DrillTypes) ->DrillMarkingSet:
    """Marks a drill set using the pre-existing answer, and updates the is_correct flag.
    
    Args: 
        user_response: list of user responses to each question for this specific drill.
        drill_set: Formatted set of drills including the question, answer, and [options].
        exercise_context: object containing exercise focuses and difficulty.
        drill_type: Enum value specifying the type of drill.
    
    Returns:
        A marked drill including correct answers, user responses, and comments.
    """
    
    request = agent_request(name=DRILL_MARKING_TYPE_CONFIG[drill_type],
                            system_prompt=DRILLS_PROMPT_CONFIG[drill_type]["mark"],
                            exercise_context=exercise_context,
                            schema=DrillMarkingSet,
                            input=user_response,
                            stimulus=[drill_set.model_dump_json()])

    result = container.llm().structured(request, DrillMarkingSet)
    return result.model_copy(update={"drill_type": drill_type})
