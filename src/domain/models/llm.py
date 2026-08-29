from typing import Any, Optional, Union

from pydantic import BaseModel

from src.domain.enums import AgentNames
from src.domain.models.exercise import ExerciseContext

LLMStimulus = Union[
    str,
    list[str],
    dict[str, Any],
    list[dict[str, Any]],
    # structured objects (e.g. ReadingGeneration, TextCorrection, Progress)
    BaseModel,
    list[BaseModel],
]
LLMInput = Union[str, list[str]]


class AgentRequest(BaseModel):
    """One call to an LLM agent.

    Lives in the domain so both the application ports and the infrastructure
    adapters can name it without either layer importing the other.
    """

    name: AgentNames | None
    system_prompt: str
    # Absent for agents that are not tied to an exercise, e.g. placement and chat.
    exercise_context: Optional[ExerciseContext] = None
    stimulus: Optional[LLMStimulus] = None
    input_text: Optional[LLMInput] = None
    output_schema: type[BaseModel] | None = None


def agent_request(
    name: AgentNames | None,
    system_prompt: str,
    exercise_context: Optional[ExerciseContext] = None,
    schema: Any | None = None,
    input: Any | None = None,
    stimulus: Any | None = None,
) -> AgentRequest:
    return AgentRequest(
        name=name,
        system_prompt=system_prompt,
        exercise_context=exercise_context,
        output_schema=schema,
        stimulus=stimulus,
        input_text=input,
    )
