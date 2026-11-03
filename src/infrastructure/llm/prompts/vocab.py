from src.domain.enums import AgentNames
from src.infrastructure.llm.contracts.learn import VocabExtraction
from src.infrastructure.llm.utils import model_prompt_example_as_json, model_schema_as_json

VOCAB_EXTRACTOR_PROMPT = f"""
Extract 5 to 10 useful Spanish lemmas a learner should remember from the text.

Rules:
- Lemmas only (dictionary form): verbs in infinitive, nouns in singular.
- Skip names, numbers, and words the learner already knows from the ignore list if given.
- gloss_en is a short English gloss, not a full definition.
- topic must be one of: travel, school, work, culture, current_events, emotions, relationships — or omit it.
- Prefer concrete, reusable words over rare or literary ones.

Return only JSON matching this schema:
{model_schema_as_json(VocabExtraction)}

Example:
{model_prompt_example_as_json(VocabExtraction)}
"""

VOCAB_PROMPT_CONFIG = {
    AgentNames.VOCAB_EXTRACTOR: VOCAB_EXTRACTOR_PROMPT,
}
