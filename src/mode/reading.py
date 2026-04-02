from src.domain.classes import CurrentSession
from src.domain.classes import CurrentSession
from src.core.display import print_big_lines, print_small_lines
from src.llm.harness import response_format
from src.llm.input import lesson_topics, AgentInputs, LessonTopics
from src.llm.enums import AgentNames
from src.llm.prompts import r_text_generation_system_prompt, r_answer_system_prompt
from src.llm.output import ReadingGeneration, QuestionMarking



def reading_mode_run(current_session: CurrentSession):
    lesson_topic = lesson_topics(current_session.current_exercise)

    print_big_lines()
    print("\nGenerating your reading text...")

    reading_prompt = text_generation(lesson_topic)
    print(reading_prompt.passage)

    user_responses = []
    for question in reading_prompt.questions:
        print_small_lines()
        user_responses.append(input(f"\nQ. {question}\nAnswer here: "))
    
    response_feedback = question_marking(user_responses, reading_prompt, lesson_topic)

    for response in response_feedback.individual_questions:
        print(f"A. {response}")
    print(response_feedback.general_feedback)

    return response_feedback.topic_score

def text_generation(lesson_topic: LessonTopics):

    agent_input = AgentInputs(
        name=AgentNames.READING_GENERATOR,
        system_prompt=r_text_generation_system_prompt,
        lesson_topics=lesson_topic
    )

    return response_format(agent_input, ReadingGeneration)


def question_marking(user_responses: list[str], reading_prompt: ReadingGeneration, lesson_topic: LessonTopics):

    agent_input = AgentInputs(
        name=AgentNames.READING_MARKING,
        system_prompt=r_answer_system_prompt,
        lesson_topics=lesson_topic,
        stimulus=reading_prompt,
        input_text=user_responses
    )

    return response_format(agent_input, QuestionMarking)


