from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from src.api.schemas.learn import LessonCard
from src.api.schemas.speaking import (
    SpeakingGenerateRequest,
    SpeakingGenerateResponse,
    SpeakingSubmitRequest,
    SpeakingSubmitResponse,
)
from src.application.services import learn as learn_file
from src.application.services import speaking as speaking_file

router = APIRouter()


@router.post("/generate", response_model=SpeakingGenerateResponse)
def generate_speaking(request: SpeakingGenerateRequest):
    try:
        prompt = speaking_file.generate_prompt(request.username)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return SpeakingGenerateResponse(prompt=prompt)


@router.post("/transcribe")
async def transcribe_speaking(username: str = Form(...), audio: UploadFile = File(...)):
    try:
        data = await audio.read()
        transcript = speaking_file.transcribe(username, data, audio.filename or "speech.webm")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return {"transcript": transcript}


@router.post("/submit", response_model=SpeakingSubmitResponse)
def submit_speaking(request: SpeakingSubmitRequest):
    try:
        corrections, feedback, verdict = speaking_file.submit_response(
            request.username, request.transcript,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return SpeakingSubmitResponse(
        corrections=corrections,
        feedback=feedback,
        counted=verdict.genuine,
        not_counted_reasons=verdict.reasons,
        lessons=[LessonCard(**row) for row in learn_file.related_for_user(request.username)],
    )
