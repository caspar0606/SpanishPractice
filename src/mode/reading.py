from pydantic import BaseModel
from src.domain.classes import CurrentSession
from src.domain.classes import CurrentSession, Progress
from src.core.display import print_big_lines
from src.llm.harness import agent_run, response_format
from src.llm.input import lesson_topics, AgentInputs
from src.llm.enums import AgentNames
from src.llm.prompts import r_text_generation_system_prompt
from src.llm.output import WritingCorrection, WritingSummary, ReadingGeneration



def reading_mode_run(current_session: CurrentSession):
    lesson_topic = lesson_topics(current_session.current_exercise)

    print_big_lines()
    print("\nGenerating your reading text...")

    reading_prompt = text_generation(lesson_topic)

    print(reading_prompt.passage)
    


def text_generation(lesson_topic: str | None):

    agent_input = AgentInputs(
        name=AgentNames.READING_GENERATOR,
        system_prompt=r_text_generation_system_prompt,
        lesson_topics=lesson_topic
    )

    return response_format(agent_input, ReadingGeneration)





