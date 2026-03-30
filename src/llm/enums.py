from enum import Enum

class AgentNames(str, Enum):
    WRITING_INSTRUCTIONS = "writing_instructions"
    WRITING_TAGGING = "writing_tagging"
    WRITING_CORRECTOR = "writing_corrector"
    WRITING_SUMMARY = "writing_summary"
    READING_GENERATOR = "reading_generator"
    READING_MARKING = "reading_marking"

