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
    name: "AgentNames | None"
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
    READING_TAGGING = "reading_tagging"
    READING_CORRECTOR = "reading_marking"
    READING_SUMMARY = "reading_summary"
    DRILLS_SENTENCE_COMPLETION_GENERATOR = "drills_sentence_completion_generator"
    DRILLS_TRANSLATION_GENERATOR = "drills_translation_generator"
    DRILLS_ERROR_CORRECTION_GENERATOR = "drills_error_correction_generator"
    DRILLS_OPTION_SELECTION_GENERATOR = "drills_option_selection_generator"
    DRILLS_OPTION_SELECTION_MARKING = "drills_option_selection_marking"
    DRILLS_ERROR_CORRECTION_MARKING = "drills_error_correction_marking"
    DRILLS_TRANSLATION_MARKING = "drills_translation_marking"
    DRILLS_SENTENCE_COMPLETION_MARKING = "drills_sentence_completion_marking"