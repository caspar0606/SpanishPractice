from typing import Optional

from pydantic import BaseModel, Field

from src.domain.enums import VocabStatus
from src.domain.models.vocab import VocabEntry


class VocabListRequest(BaseModel):
    username: str


class VocabListResponse(BaseModel):
    items: list[VocabEntry]
    due_count: int = 0


class VocabMarkRequest(BaseModel):
    username: str
    lemma: str
    status: Optional[VocabStatus] = None
    starred: Optional[bool] = None


class VocabReviewItem(BaseModel):
    lemma: str
    gloss_en: str


class VocabReviewResponse(BaseModel):
    items: list[VocabReviewItem]


class VocabReviewResult(BaseModel):
    lemma: str
    guess: str = ""


class VocabReviewSubmitRequest(BaseModel):
    username: str
    results: list[VocabReviewResult] = Field(default_factory=list)
