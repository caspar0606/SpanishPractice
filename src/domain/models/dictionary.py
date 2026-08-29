"""A Spanish word looked up in an external dictionary."""

from pydantic import BaseModel, Field


class DictionaryEntry(BaseModel):
    headword: str
    part_of_speech: str = ""
    glosses: list[str] = Field(default_factory=list)


class DictionaryLookup(BaseModel):
    query: str
    found: bool = False
    entries: list[DictionaryEntry] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)
