from pydantic import BaseModel, Field

from src.domain.models.dictionary import DictionaryEntry


class TranslateResponse(BaseModel):
    query: str
    found: bool = False
    entries: list[DictionaryEntry] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)
