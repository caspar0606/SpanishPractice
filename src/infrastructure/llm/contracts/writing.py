from pydantic import BaseModel

class WritingSummary(BaseModel):
    tense_edits: str
    grammar_edits: str
    topic_edits: str
    general_feedback: str
