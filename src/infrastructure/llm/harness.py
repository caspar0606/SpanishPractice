from pydantic import BaseModel
from typing import Any, TypeVar

from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain.messages import HumanMessage

from src.domain.models.exercise import ExerciseContext
from src.infrastructure.llm.contracts.shared import AgentInputs, AgentNames
from src.infrastructure.llm.utils import serialise_for_prompt



def agent_run(agent_inputs: AgentInputs):
    model = init_chat_model(model = "gpt-5.4-mini")

    agent = create_agent(
        model=model,
        system_prompt=agent_inputs.system_prompt,
        response_format=agent_inputs.output_schema,
        name=agent_inputs.name
    )

    messages = []

    if agent_inputs.exercise_context.areas_of_focus is not None:
        messages.append(HumanMessage(content=f"Lesson context:\n{serialise_for_prompt(agent_inputs.exercise_context.areas_of_focus)}"))

    if agent_inputs.exercise_context.exercise_config is not None:
        messages.append(HumanMessage(content=f"Exercise config:\n{serialise_for_prompt(agent_inputs.exercise_context.exercise_config)}"))

    if agent_inputs.stimulus is not None:
        messages.append(HumanMessage(content=f"User stimulus:\n{serialise_for_prompt(agent_inputs.stimulus)}"))
    
    if agent_inputs.input_text is not None:
        messages.append(HumanMessage(content=f"User response:\n{serialise_for_prompt(agent_inputs.input_text)}"))


    response = agent.invoke({"messages": messages})
    
    return response


def message_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict):
                parts.append(str(block.get("text") or ""))
            else:
                parts.append(str(getattr(block, "text", "") or ""))
        return "".join(parts)
    return str(content)


T = TypeVar("T", bound=BaseModel)
def response_format(agent_input: AgentInputs, schema: type[T]) -> T:

    response = agent_run(agent_input)
    structured = response.get("structured_response")
    if isinstance(structured, schema):
        return structured
    if structured is not None:
        return schema.model_validate(structured)

    last = response["messages"][-1]
    return schema.model_validate_json(message_text(last.content))


def agent_inputs(
    name: AgentNames | None,
    system_prompt: str,
    exercise_context: ExerciseContext,
    schema: Any | None = None,
    input: Any | None = None,
    stimulus: Any | None = None
):
    return AgentInputs(
        name=name,
        system_prompt=system_prompt,
        exercise_context=exercise_context,
        output_schema=schema,
        stimulus=stimulus,
        input_text=input
    )