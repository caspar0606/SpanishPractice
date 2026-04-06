from src.application.exercise_selection import lesson_topics
from src.domain.models.exercise import LessonTopics
from src.domain.models.progress import Progress
from src.infrastructure.llm.contracts.reading import ReadingGeneration, QuestionMarking
from src.infrastructure.llm.contracts.shared import AgentNames
from src.infrastructure.llm.prompts.reading import r_answer_system_prompt, r_generation_system_prompt
from src.infrastructure.llm.prompts.writing import w_tagging_system_prompt
from src.infrastructure.llm.harness import agent_inputs, response_format
from src.domain.models.session import Session
from src.infrastructure.persistence.session_storage import store_exercise

def reading_mode_run(current_session: Session):
    lesson_topic = lesson_topics(current_session.current_exercise)

    reading_prompt = text_generation(lesson_topic)
    print(reading_prompt.passage)

    user_responses = []
    for question in reading_prompt.questions:
        user_responses.append(input(f"\nQ. {question}\nAnswer here: "))

    progress = response_tagging(user_responses, reading_prompt, lesson_topic)
    
    response_feedback = question_marking(user_responses, reading_prompt, lesson_topic)

    for response in response_feedback.individual_questions:
        print(f"A. {response}")
    print(response_feedback.general_feedback)

    exercise_storage = store_exercise(current_session.current_exercise, progress, reading_prompt, user_responses, response_feedback)
                                      
    return exercise_storage


def text_generation(lesson_topic: LessonTopics):

    agent_input = agent_inputs(AgentNames.READING_GENERATOR, system_prompt=r_generation_system_prompt, 
                               lesson_topic=lesson_topic, schema=ReadingGeneration)

    return response_format(agent_input, ReadingGeneration)



def response_tagging(user_responses: list[str], reading_prompt: ReadingGeneration, lesson_topic: LessonTopics):

    agent_input = agent_inputs(AgentNames.WRITING_TAGGING, system_prompt=w_tagging_system_prompt, lesson_topic=lesson_topic,
                               input=user_responses, stimulus=reading_prompt)

    return response_format(agent_input, Progress)

def question_marking(user_responses: list[str], reading_prompt: ReadingGeneration, lesson_topic: LessonTopics):

    agent_input = agent_inputs(AgentNames.READING_MARKING, r_answer_system_prompt, 
                               lesson_topic=lesson_topic, stimulus=reading_prompt, input=user_responses)

    return response_format(agent_input, QuestionMarking)
