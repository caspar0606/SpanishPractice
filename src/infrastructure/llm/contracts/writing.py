from typing import ClassVar

from pydantic import BaseModel

class WritingSummary(BaseModel):
    _EXAMPLE: ClassVar[dict] = {
        "tense_edits": "Mostly consistent tense usage; review one past-tense form.",
        "grammar_edits": "Watch gender agreement on adjectives and articles.",
        "topic_edits": "Vocabulary stayed on topic; add one more topic-specific phrase next time.",
        "general_feedback": "Clear ideas and mostly correct sentences. Focus on agreement and a couple verb forms.",
    }

    tense_edits: str
    grammar_edits: str
    topic_edits: str
    general_feedback: str

    @classmethod
    def example_json(cls) -> dict:
        return cls._EXAMPLE.copy()
