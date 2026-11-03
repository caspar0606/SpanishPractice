import re

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile

from src.api.deps import current_username, limited
from src.api.errors import http_from_value_error
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

MAX_AUDIO_BYTES = 2 * 1024 * 1024
_SAFE_NAME = re.compile(r"^[\w.\-]{1,80}$")


@router.post("/generate", response_model=SpeakingGenerateResponse)
def generate_speaking(
    request: SpeakingGenerateRequest,
    username: str = Depends(limited("speaking_generate", 20)),
):
    try:
        prompt = speaking_file.generate_prompt(username)
    except ValueError as e:
        raise http_from_value_error(e) from e
    return SpeakingGenerateResponse(prompt=prompt)


@router.post("/transcribe")
async def transcribe_speaking(
    request: Request,
    audio: UploadFile = File(...),
    username: str = Depends(limited("speaking_transcribe", 10)),
):
    content_length = request.headers.get("content-length")
    if content_length:
        try:
            if int(content_length) > MAX_AUDIO_BYTES + 8192:
                raise HTTPException(
                    status_code=413,
                    detail="Recording is too large. Try a shorter clip.",
                )
        except ValueError:
            pass
    data = await audio.read(MAX_AUDIO_BYTES + 1)
    if len(data) > MAX_AUDIO_BYTES:
        raise HTTPException(
            status_code=413,
            detail="Recording is too large. Try a shorter clip.",
        )
    filename = audio.filename or "speech.webm"
    if not _SAFE_NAME.fullmatch(filename):
        filename = "speech.webm"
    try:
        transcript = speaking_file.transcribe(username, data, filename)
    except ValueError as e:
        raise http_from_value_error(e) from e
    return {"transcript": transcript}


@router.post("/submit", response_model=SpeakingSubmitResponse)
def submit_speaking(request: SpeakingSubmitRequest, username: str = Depends(current_username)):
    try:
        corrections, feedback, verdict = speaking_file.submit_response(
            username, request.transcript,
        )
    except ValueError as e:
        raise http_from_value_error(e) from e
    return SpeakingSubmitResponse(
        corrections=corrections,
        feedback=feedback,
        counted=verdict.genuine,
        not_counted_reasons=verdict.reasons,
        lessons=[LessonCard(**row) for row in learn_file.related_for_user(username)],
    )
