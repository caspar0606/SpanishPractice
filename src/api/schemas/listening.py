from pydantic import BaseModel, Field

from src.api.schemas.learn import LessonCard
from src.infrastructure.llm.contracts.reading import QuestionMarking


class ListeningGenerateRequest(BaseModel):
    username: str


class ListeningGenerateResponse(BaseModel):
    clip_id: str
    audio_url: str
    questions: list[str]
    turn_count: int = 0


class ListeningSubmitRequest(BaseModel):
    username: str
    answers: list[str] = Field(default_factory=list)


class ListeningSubmitResponse(BaseModel):
    feedback: QuestionMarking
    transcript: str
    counted: bool = True
    not_counted_reasons: list[str] = Field(default_factory=list)
    lessons: list[LessonCard] = Field(default_factory=list)
