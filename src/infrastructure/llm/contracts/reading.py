from pydantic import BaseModel


class ReadingGeneration(BaseModel):
    passage: str
    questions: list[str]

class QuestionMarking(BaseModel):
    individual_questions: list[str]
    general_feedback: str