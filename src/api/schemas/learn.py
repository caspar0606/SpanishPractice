from pydantic import BaseModel, Field

from src.domain.models.lesson import Lesson


class LessonCard(BaseModel):
    key: str
    axis: str
    title_en: str
    summary: str = ""


class LearnIndexResponse(BaseModel):
    lessons: list[LessonCard]


class LessonResponse(BaseModel):
    lesson: Lesson


class ChatAskRequest(BaseModel):
    username: str
    question: str


class ChatAskResponse(BaseModel):
    answer_en: str
    known: bool = True
    lesson_keys: list[str] = Field(default_factory=list)
    lessons: list[LessonCard] = Field(default_factory=list)
    history: list[dict] = Field(default_factory=list)


class ChatHistoryRequest(BaseModel):
    username: str
