"""A browseable grammar or tense note loaded from content JSON."""

from typing import Optional

from pydantic import BaseModel, Field


class LessonExample(BaseModel):
    es: str
    en: str
    note: str = ""


class Lesson(BaseModel):
    key: str
    axis: str
    title_en: str
    when_to_use: list[str] = Field(default_factory=list)
    rule: str = ""
    table: dict[str, dict[str, str]] = Field(default_factory=dict)
    examples: list[LessonExample] = Field(default_factory=list)
    common_mistake: str = ""

    def summary(self) -> str:
        if self.when_to_use:
            return self.when_to_use[0]
        if self.rule:
            return self.rule
        return self.title_en

    def searchable_text(self) -> str:
        chunks = [
            self.key,
            self.title_en,
            self.axis,
            self.rule,
            self.common_mistake,
            *self.when_to_use,
        ]
        for example in self.examples:
            chunks.extend([example.es, example.en, example.note])
        return " ".join(chunks).lower()
