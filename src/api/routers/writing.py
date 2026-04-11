from fastapi import APIRouter, HTTPException

from src.application.services import writing as writing_file
from src.api.schemas.writing import WritingGenerationRequest, WritingGenerationResponse, WritingSummaryResponse, WritingUserRequest

router = APIRouter()

@router.post("/generate", response_model=WritingGenerationResponse)
def generate_writing_instruction(request: WritingGenerationRequest):
    try:
        result = writing_file.generate_instructions(request.username)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return WritingGenerationResponse(
        prompt=result
    )

@router.post("/submit", response_model=WritingSummaryResponse)
def submit_text(request: WritingUserRequest):
    try:
        result = writing_file.submit_response(request.user_response, request.username)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return WritingSummaryResponse(
        corrections=result[0],
        feedback=result[1]
    )

