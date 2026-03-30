from dotenv import load_dotenv
import os

from src.llm.enums import AgentNames

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

from pydantic import BaseModel
from typing import TypeVar
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from src.llm.input import AgentInputs
from langchain.messages import SystemMessage, HumanMessage, AIMessage


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
        messages.append(HumanMessage(content=f"Lesson context:\n{agent_inputs.lesson_topics}"))

    if agent_inputs.input_text is not None:
        messages.append(HumanMessage(content=f"Input text:\n{agent_inputs.input_text}"))

    response = agent.invoke({"messages": messages})
    
    return response

def create_model(model_inputs: str):
    return init_chat_model(model = "gpt-5.4-mini")



T = TypeVar("T", bound=BaseModel)

def response_format(agent_input: AgentInputs, schema: type[T]) -> T:

    response = agent_run(agent_input)
    ai_message = response["messages"][-1].content
    return schema.model_validate_json(ai_message)


def agent_inputs(name: AgentNames, system_prompt: str, lesson_topic: str, schema: type[BaseModel], input: list[str]):
    return AgentInputs(
        name=name,
        system_prompt=system_prompt,
        lesson_topics=lesson_topic,
        output_schema=schema,
        input_text=input
    )