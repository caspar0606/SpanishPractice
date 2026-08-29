from fastapi import APIRouter, HTTPException

from src.api.schemas.learn import LessonCard
from src.api.schemas.listening import (
    ListeningGenerateRequest,
    ListeningGenerateResponse,
    ListeningSubmitRequest,
    ListeningSubmitResponse,
)
from src.application.services import learn as learn_file
from src.application.services import listening as listening_file

router = APIRouter()


@router.post("/generate", response_model=ListeningGenerateResponse)
def generate_listening(request: ListeningGenerateRequest):
    try:
        result = listening_file.generate_clip(request.username)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return ListeningGenerateResponse(**result)


@router.post("/submit", response_model=ListeningSubmitResponse)
def submit_listening(request: ListeningSubmitRequest):
    try:
        feedback, verdict, transcript = listening_file.submit_response(
            request.username, request.answers,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return ListeningSubmitResponse(
        feedback=feedback,
        transcript=transcript,
        counted=verdict.genuine,
        not_counted_reasons=verdict.reasons,
        lessons=[LessonCard(**row) for row in learn_file.related_for_user(request.username)],
    )
