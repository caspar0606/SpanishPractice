from typing import Optional

from pydantic import BaseModel, Field, field_validator

from src.domain.enums import DrillTypes
from src.domain.models.progress import ComputeStats


class DrillItem(BaseModel):
    prompt: str
    answer: str
    options: list[str] | None = None

class DrillSet(BaseModel):
    drill_type: DrillTypes
    drills: list[DrillItem]

class Drills(BaseModel):
    drill_sets: dict[DrillTypes, DrillSet]

class DrillMarking(BaseModel):
    prompt: str
    answer: str
    user_response: str
    comment: Optional[str] 
    is_correct: bool

class DrillMarkingSet(BaseModel):
    drill_type: DrillTypes
    marked_drills: list[DrillMarking]
    # LLM structured output often returns "stats": null; we compute stats in code anyway.
    stats: ComputeStats = Field(default_factory=ComputeStats)

    @field_validator("stats", mode="before")
    @classmethod
    def stats_null_to_default(cls, v: object) -> object:
        if v is None:
            return ComputeStats()
        return v

class MarkedDrills(BaseModel):
    marked_drill_sets: list[DrillMarkingSet]
    stats: ComputeStats

class UserDrillResponses(BaseModel):
    responses: dict[DrillTypes, list[str]]
