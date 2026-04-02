from src.core.display import print_big_lines
from src.llm.input import lesson_topics, AgentInputs, LessonTopics
from src.llm.enums import AgentNames
from src.llm.prompts import w_instruction_system_prompt, w_tagging_system_prompt, w_correcting_system_prompt, w_summary_system_prompt
from src.llm.output import WritingCorrection, WritingSummary

from src.core.session_storage import store_exercise

from src.domain.classes import Session, Progress

def writing_mode_run(current_session: Session):
    lesson_topic = lesson_topics(current_session.current_exercise)

    print_big_lines()
    print("\nGenerating your writing instructions...")
    writing_instruction = instruction_generation(lesson_topic)

    print(f"\nHere is your writing prompt, ¡Buena Suerte! \n\n {writing_instruction}")

    user_response = input("\nPaste/write your response here: ")

    print(f"\nTagging the response...")
    exercise_counts = progress_tagging(user_response, lesson_topic)

    print_big_lines()
    print(f"Correcting the text...\n")
    corrected_text = text_correction(user_response, lesson_topic, writing_instruction)
    print(corrected_text.corrected_version)

    print_big_lines()
    print(f"Summarising corrections...\n")
    summaries = correction_summary(corrected_text, lesson_topic, exercise_counts)
    print(summaries.general_feedback)

    exercise_storage = store_exercise(current_session.current_exercise, exercise_counts, writing_instruction, user_response, summaries)

    return exercise_storage
    
from src.llm.harness import agent_inputs, agent_run, response_format

def instruction_generation(lesson_topic: LessonTopics):    

    agent_input = AgentInputs(
        name=AgentNames.WRITING_INSTRUCTIONS,
        system_prompt=w_instruction_system_prompt,
        lesson_topics=lesson_topic
    )

    response = agent_run(agent_input)
    return response["messages"][-1].content

def progress_tagging(user_response: str, lesson_topic: LessonTopics):

    agent_input = agent_inputs(name=AgentNames.WRITING_TAGGING, system_prompt=w_tagging_system_prompt, 
                               lesson_topic=lesson_topic, input=user_response, schema=Progress)

    return response_format(agent_input, Progress)

def text_correction(user_response: str, lesson_topic: LessonTopics, writing_instruction: str):

    agent_input = agent_inputs(AgentNames.WRITING_CORRECTOR, system_prompt=w_correcting_system_prompt, 
                               lesson_topic=lesson_topic, schema=WritingCorrection, stimulus=writing_instruction,input=user_response)

    return response_format(agent_input, WritingCorrection)

def correction_summary(edits: WritingCorrection, lesson_topic: LessonTopics, exercise_counts: Progress):

    agent_input = agent_inputs(name=AgentNames.WRITING_SUMMARY, system_prompt=w_summary_system_prompt,lesson_topic=lesson_topic,
        schema=WritingSummary, stimulus=[edits.model_dump_json(), exercise_counts.model_dump_json()])

    return response_format(agent_input, WritingSummary)
