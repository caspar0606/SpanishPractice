from typing import ClassVar

from pydantic import BaseModel, Field


class PlacementAssessment(BaseModel):
    """Two scalar signals plus an English note.

    Banding itself is deterministic in `src/domain/rules/placement.py`, so the
    model is only asked to judge the samples, never to pick a level.
    """

    _EXAMPLE: ClassVar[dict] = {
        "writing_signal": 0.42,
        "reading_signal": 0.66,
        "notes_en": "Comfortable with present tense and everyday vocabulary. Past tense endings are inconsistent and sentences stay short.",
    }

    writing_signal: float = Field(
        ge=0.0,
        le=1.0,
        description="0 means no usable Spanish, 1 means confident upper-intermediate writing.",
    )
    reading_signal: float = Field(
        ge=0.0,
        le=1.0,
        description="Share of the reading questions answered correctly and completely.",
    )
    notes_en: str = Field(description="Two or three sentences in English about what the learner can and cannot do yet.")

    @classmethod
    def example_json(cls) -> dict:
        return cls._EXAMPLE.copy()
