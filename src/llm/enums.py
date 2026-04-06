from enum import Enum

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
    



class DrillTypes(str, Enum):
    SENTENCE_COMPLETION = "sentence_completion"
    TRANSLATION = "translate"
    ERROR_CORRECTION = "error_correction"
    OPTION_SELECTION = "option_selection"
