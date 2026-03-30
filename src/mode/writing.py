from src.core.display import print_big_lines
from src.domain.classes import CurrentSession
from src.llm.harness import agent_run
from src.llm.input import lesson_topics, AgentInputs
from src.llm.enums import AgentNames
from src.llm.prompts import w_instruction_system_prompt



def writing_mode_run(current_session: CurrentSession):

    print_big_lines()
    print("\nGenerating your writing instructions...")
    writing_instruction = instruction_generation(current_session)

    print(f"\nHere is your writing prompt, ¡Buena Suerte! \n\n {writing_instruction}")

def instruction_generation(current_session: CurrentSession):
    lesson_topic = lesson_topics(current_session.current_exercise)
    

    agent_input = AgentInputs(
        name=AgentNames.WRITING_INSTRUCTIONS,
        system_prompt=w_instruction_system_prompt,
        lesson_topics=lesson_topic
    )

    response = agent_run(agent_input)
    
    return response["messages"][-1].content
    