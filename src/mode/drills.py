from src.core.display import print_big_lines
from src.domain.enums import DifficultyLevels
from src.llm.harness import agent_inputs, response_format
from src.llm.input import lesson_topics, AgentInputs, LessonTopics
from src.llm.enums import AgentNames, DrillTypes
from src.llm.prompts import d_translate_generator_system_prompt, d_sentence_complete_generator_system_prompt, \
                            d_error_correct_generator_system_prompt, d_option_select_generator_system_prompt, \
                            d_error_correct_marker_system_prompt, d_option_select_marker_system_prompt, \
                            d_sentence_complete_marker_system_prompt, d_translate_marker_system_prompt

from src.llm.output import DrillMarkingSet, Drills, MarkedDrills, UserDrillResponses, WritingCorrection, WritingSummary, DrillSet

from src.core.session_storage import store_exercise

from src.domain.classes import ComputeStats, ExerciseStorage, Session, Progress
from src.mode.writing import correction_summary, instruction_generation, progress_tagging, text_correction

def drills_mode_run(current_session: Session):
    lesson_topic = lesson_topics(current_session.current_exercise)
    lesson_topic.word_count = 0

    drills = create_drills(lesson_topic)

    user_responses = UserDrillResponses(responses={})

    marked_drills = mark_drill_sets(user_responses, drills, lesson_topic)
    
    return marked_drills

#def submit_drills(current_session: Session):


def create_drills(lesson_topic: LessonTopics):
    question_set = QUESTION_NUMBER_CONFIG[lesson_topic.difficulty]


    return Drills(drill_sets={
                drill_type: generate_drill_set(lesson_topic, question_set, drill_type) 
                for drill_type in DrillTypes
                }
            )


#def submit_drills(user_response, drills: Drills, lesson_topic: LessonTopics):


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


QUESTION_NUMBER_CONFIG = {
    DifficultyLevels.BEGINNER: {
        DrillTypes.SENTENCE_COMPLETION: 6,
        DrillTypes.OPTION_SELECTION: 7,
        DrillTypes.ERROR_CORRECTION: 4,
        DrillTypes.TRANSLATION: 3
    },
    DifficultyLevels.NOVICE: {
        DrillTypes.SENTENCE_COMPLETION: 5,
        DrillTypes.OPTION_SELECTION: 6,
        DrillTypes.ERROR_CORRECTION: 5,
        DrillTypes.TRANSLATION: 4
    },
    DifficultyLevels.INTERMEDIATE: {
        DrillTypes.SENTENCE_COMPLETION: 4,
        DrillTypes.OPTION_SELECTION: 5,
        DrillTypes.ERROR_CORRECTION: 6,
        DrillTypes.TRANSLATION: 5
    }
}

DRILLS_PROMPT_CONFIG = {
    DrillTypes.SENTENCE_COMPLETION: {
        "generate": d_sentence_complete_generator_system_prompt,
        "mark": d_sentence_complete_marker_system_prompt
    },
    DrillTypes.OPTION_SELECTION: {
        "generate": d_option_select_generator_system_prompt,
        "mark": d_option_select_marker_system_prompt
    },
    DrillTypes.ERROR_CORRECTION: {
        "generate": d_error_correct_generator_system_prompt,
        "mark": d_error_correct_marker_system_prompt
    },
    DrillTypes.TRANSLATION: {
        "generate": d_translate_generator_system_prompt,
        "mark": d_translate_marker_system_prompt
    }
}