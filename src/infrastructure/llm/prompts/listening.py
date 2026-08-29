from src.domain.enums import AgentNames
from src.infrastructure.llm.contracts.listening import ListeningGeneration
from src.infrastructure.llm.utils import model_prompt_example_as_json, model_schema_as_json
from src.domain.models.exercise import ExerciseContext

LISTENING_GENERATOR_PROMPT = f"""
You write short spoken Spanish dialogues for learners, plus comprehension questions.

OUTPUT:
{model_schema_as_json(ListeningGeneration)}

Example:
{model_prompt_example_as_json(ListeningGeneration)}

INPUT:
{model_schema_as_json(ExerciseContext)}

Requirements:
- 3 to 8 short spoken turns between two named people.
- Follow exercise_config.level (0–8) and level_hint. Level 2 is very simple; level 8 is richer but still clear speech.
- Honour any requested topics. Tenses and grammar must appear naturally; never name them.
- The whole dialogue should be about the given word_count, ±20%.
- Questions: 2 or 3, in Spanish, answerable from what was said.
- No stage directions, no English, no JSON keys outside the schema.
"""

LISTENING_PROMPT_CONFIG = {
    AgentNames.LISTENING_GENERATOR: LISTENING_GENERATOR_PROMPT,
}
