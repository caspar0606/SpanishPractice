from src.application.exercise_selection import lesson_topics
from src.domain.enums import DrillTypes
from src.domain.models.exercise import LessonTopics
from src.domain.rules import QUESTION_NUMBER_CONFIG
from src.infrastructure.llm.contracts.drills import DrillMarkingSet, Drills, MarkedDrills, UserDrillResponses, DrillSet
from src.infrastructure.llm.contracts.shared import AgentNames
from src.infrastructure.llm.prompts.drills import DRILLS_PROMPT_CONFIG
from src.infrastructure.llm.harness import agent_inputs, response_format
from src.domain.models.session import Session
from src.domain.models.progress import ComputeStats


def drills_mode_run(current_session: Session):
    lesson_topic = lesson_topics(current_session.current_exercise)
    lesson_topic.word_count = 0

    drills = create_drills(lesson_topic)

    user_responses = UserDrillResponses(responses={})

    marked_drills = mark_drill_sets(user_responses, drills, lesson_topic)
    
    return marked_drills


def create_drills(lesson_topic: LessonTopics):
    question_set = QUESTION_NUMBER_CONFIG[lesson_topic.difficulty]


    return Drills(drill_sets={
                drill_type: generate_drill_set(lesson_topic, question_set, drill_type) 
                for drill_type in DrillTypes
                }
            )


def generate_drill_set(lesson_topic: LessonTopics, question_set: dict, drill_type: DrillTypes) -> DrillSet:

    agent_input = agent_inputs(name=AgentNames.SENTENCE_COMPLETION_GENERATOR, 
                               system_prompt=DRILLS_PROMPT_CONFIG[drill_type]["generate"],
                               lesson_topic=lesson_topic,
                               schema=DrillSet,
                               stimulus=f"number_of_questions: {question_set[drill_type]}")
    
    return response_format(agent_input, DrillSet)

def mark_drill_sets(user_responses: UserDrillResponses, drills: Drills, lesson_topic: LessonTopics) -> MarkedDrills:

    corrected_drills = [mark_drill_set(user_responses.responses[drill_type], drills.drill_sets[drill_type], 
                                    lesson_topic, drill_type) for drill_type in DrillTypes]
    
    for drill_set in corrected_drills:
        drill_set.stats = ComputeStats(
        total_attempts=len(drill_set.marked_drills),
        correct_attempts=sum(d.is_correct for d in drill_set.marked_drills))

    marked_drills = MarkedDrills(marked_drill_sets=corrected_drills, 
                                 stats=ComputeStats(
                                     total_attempts=sum(drill_set.stats.total_attempts for drill_set in corrected_drills),
                                     correct_attempts=sum(drill_set.stats.correct_attempts for drill_set in corrected_drills)))
    
    return marked_drills
            

def mark_drill_set(user_response: list[str], drill_set: DrillSet, lesson_topic: LessonTopics, drill_type: DrillTypes):

    agent_input = agent_inputs(name=AgentNames.SENTENCE_COMPLETION_GENERATOR, 
                               system_prompt=DRILLS_PROMPT_CONFIG[drill_type]["mark"],
                               lesson_topic=lesson_topic,
                               schema=DrillMarkingSet,
                               input=user_response,
                               stimulus=[drill_set.model_dump_json()])
    
    return response_format(agent_input, DrillMarkingSet)
