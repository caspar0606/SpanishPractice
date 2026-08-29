from fastapi import APIRouter, HTTPException

from src.api.schemas.learn import LearnIndexResponse, LessonCard, LessonResponse
from src.application.services import learn as learn_file

router = APIRouter()


@router.get("/index", response_model=LearnIndexResponse)
def learn_index():
    return LearnIndexResponse(lessons=[LessonCard(**row) for row in learn_file.index()])


@router.get("/lesson/{key}", response_model=LessonResponse)
def learn_lesson(key: str):
    try:
        lesson = learn_file.get(key)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    return LessonResponse(lesson=lesson)
