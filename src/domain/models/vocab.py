"""Per-user vocabulary the learner has met in real exercises."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from src.domain.enums import Topics, VocabStatus


class VocabEntry(BaseModel):
    lemma: str
    gloss_en: str
    topic: Optional[Topics] = None
    times_seen: int = 1
    times_correct: int = 0
    status: VocabStatus = VocabStatus.NEW
    starred: bool = False
    next_review: Optional[datetime] = None
    added_at: datetime = Field(default_factory=datetime.now)
