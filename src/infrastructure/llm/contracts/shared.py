from enum import Enum
from typing import Optional, Union
from pydantic import BaseModel

from src.domain.models.exercise import ExerciseContext
from src.infrastructure.llm.contracts.reading import ReadingGeneration

LLMStimulus = Union[ReadingGeneration,list[str], str]
LLMInput = Union[str, list[str], ]
    
class ModelInputs(BaseModel):
    model_name: str
    temperature: float
    max_tokens: Optional[int]

class AgentInputs(BaseModel):
    name: "AgentNames"
    exercise_context: ExerciseContext 
    system_prompt: str
    stimulus: Optional[LLMStimulus] = None
    input_text: Optional[LLMInput] = None
    output_schema: type[BaseModel] | None = None

class AgentNames(str, Enum):
    WRITING_INSTRUCTIONS = "writing_instructions"
    WRITING_TAGGING = "writing_tagging"
    WRITING_CORRECTOR = "writing_corrector"
    WRITING_SUMMARY = "writing_summary"
    READING_GENERATOR = "reading_generator"
    READING_MARKING = "reading_marking"
    SENTENCE_COMPLETION_GENERATOR = "sentence_completion_generator"
    TRANSLATE_GENERATOR = "translate_generator"
    ERROR_CORRECTION_GENERATOR = "error_correction_generator"
    OPTION_SELECTION_GENERATOR = "option_selection_generator"
