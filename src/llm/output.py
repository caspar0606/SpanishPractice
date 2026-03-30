from pydantic import BaseModel
from src.domain.classes import Tenses, Grammar, Topics

class Edit(BaseModel):
    original_text: str
    corrected_text: str
    reason: str

class WritingCorrection(BaseModel):
    corrected_version: str
    tense_errors: dict[Tenses, list[Edit]]
    grammar_errors: dict[Grammar, list[Edit]]
    topic_errors: dict[Topics, list[Edit]]
    typos: list[Edit]
    other_mistakes: list[Edit]