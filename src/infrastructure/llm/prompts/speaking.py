from src.domain.enums import AgentNames
from src.infrastructure.llm.contracts.text_correction import TextCorrection
from src.infrastructure.llm.utils import model_prompt_example_as_json, model_schema_as_json
from src.domain.models.exercise import ExerciseContext

SPEAKING_INSTRUCTIONS_PROMPT = """
You write a short spoken Spanish task for a learner.

The learner will record their answer, not write it. Keep the brief to two or three
spoken-style sentences of Spanish: a situation, then what they should say.

Honour exercise_config.level (0–8) and level_hint, and any requested topics.
Aim at about the given word_count for their spoken answer, mentioned in everyday Spanish if it fits.

OUTPUT: Spanish only. No JSON, no English, no tense names.
"""

SPEAKING_CORRECTOR_PROMPT = f"""
You correct a learner's spoken Spanish from a transcript.

Ignore pronunciation, accent, and Whisper artefacts (odd spacing, missed punctuation).
Score grammar, tense choice, agreement, and whether they answered the task.

INPUT exercise context:
{model_schema_as_json(ExerciseContext)}

OUTPUT:
{model_schema_as_json(TextCorrection)}

Example:
{model_prompt_example_as_json(TextCorrection)}

Do not comment on how they sounded. Treat the transcript as writing that may have
speech-to-text noise.
"""

SPEAKING_PROMPT_CONFIG = {
    AgentNames.SPEAKING_INSTRUCTIONS: SPEAKING_INSTRUCTIONS_PROMPT,
    AgentNames.SPEAKING_CORRECTOR: SPEAKING_CORRECTOR_PROMPT,
}
