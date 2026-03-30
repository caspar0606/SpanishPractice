from src.core.display import print_big_lines
from src.domain.classes import CurrentSession, Progress
from src.llm.harness import agent_run
from src.llm.input import lesson_topics, AgentInputs
from src.llm.enums import AgentNames
from src.llm.prompts import w_instruction_system_prompt, w_tagging_system_prompt, w_correcting_system_prompt
from src.llm.output import WritingCorrection

def writing_mode_run(current_session: CurrentSession):
    lesson_topic = lesson_topics(current_session.current_exercise)

    print_big_lines()
    print("\nGenerating your writing instructions...")
    writing_instruction = instruction_generation(lesson_topic)

    print(f"\nHere is your writing prompt, ¡Buena Suerte! \n\n {writing_instruction}")

    user_response = input("\nPaste/write your response here: ")

    print(f"\nAnalysing your response...")
    exercise_counts = progress_tagging(user_response, lesson_topic)
    print(exercise_counts)

    corrected_version = text_correction(user_response, lesson_topic, writing_instruction)
    print(corrected_version)

def instruction_generation(lesson_topic: str | None):    

    agent_input = AgentInputs(
        name=AgentNames.WRITING_INSTRUCTIONS,
        system_prompt=w_instruction_system_prompt,
        lesson_topics=lesson_topic
    )

    response = agent_run(agent_input)
    
    return response["messages"][-1].content

def progress_tagging(user_response: str, lesson_topic: str | None):

    agent_input = AgentInputs(
        name=AgentNames.WRITING_TAGGING,
        system_prompt=w_tagging_system_prompt,
        lesson_topics=lesson_topic,
        input_text=[user_response],
        output_schema=Progress
    )

    response = agent_run(agent_input)

    return response["messages"][-1].content

def text_correction(user_response: str, lesson_topic: str | None, writing_instruction: str):

    agent_input = AgentInputs(
        name=AgentNames.WRITING_CORRECTOR,
        system_prompt=w_correcting_system_prompt,
        lesson_topics=lesson_topic,
        output_schema=WritingCorrection,
        input_text=[user_response, writing_instruction]
    )

    response = agent_run(agent_input)

    return response["messages"][-1].content