from dotenv import load_dotenv
import os

from src.llm.enums import AgentNames

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

from pydantic import BaseModel
from typing import Any, TypeVar
import json

from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from src.llm.input import AgentInputs, LessonTopics
from langchain.messages import HumanMessage


def agent_run(agent_inputs: AgentInputs):
    model = create_model("placeholder")

    agent = create_agent(
        model=model,
        system_prompt=agent_inputs.system_prompt,
        response_format=agent_inputs.output_schema,
        name=agent_inputs.name
    )

    messages = []

    if agent_inputs.lesson_topics is not None:
        messages.append(HumanMessage(content=f"Lesson context:\n{serialise_for_prompt(agent_inputs.lesson_topics)}"))

    if agent_inputs.stimulus is not None:
        messages.append(HumanMessage(content=f"User stimulus:\n{serialise_for_prompt(agent_inputs.stimulus)}"))
    
    if agent_inputs.input_text is not None:
        messages.append(HumanMessage(content=f"User response:\n{serialise_for_prompt(agent_inputs.input_text)}"))


    response = agent.invoke({"messages": messages})
    
    return response



def create_model(model_inputs: str):
    return init_chat_model(model = "gpt-5.4-mini")


T = TypeVar("T", bound=BaseModel)
def response_format(agent_input: AgentInputs, schema: type[T]) -> T:

    response = agent_run(agent_input)
    ai_message = response["messages"][-1].content
    return schema.model_validate_json(ai_message)


def serialise_for_prompt(value) -> str:
    if value is None:
        return ""

    if isinstance(value, BaseModel):
        return json.dumps(value.model_dump(), indent=2, ensure_ascii=False)

    if isinstance(value, (dict, list)):
        return json.dumps(value, indent=2, ensure_ascii=False)

    return str(value)

def agent_inputs(
    name: AgentNames,
    system_prompt: str,
    lesson_topic: LessonTopics | None = None,
    schema: Any | None = None,
    input: Any | None = None,
    stimulus: Any | None = None
):
    return AgentInputs(
        name=name,
        system_prompt=system_prompt,
        lesson_topics=lesson_topic,
        output_schema=schema,
        stimulus=stimulus,
        input_text=input
    )