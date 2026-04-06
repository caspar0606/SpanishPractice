from fastapi import APIRouter

from src.application.services import writing as writing_file
from src.api.schemas.writing import WritingGenerationRequest, WritingGenerationResponse, WritingSummaryResponse, WritingUserRequest

router = APIRouter()

@router.post("/generate", response_model=WritingGenerationResponse)
def generate_writing_instruction(request: WritingGenerationRequest):
    result = writing_file.generate_instructions(request.username)

    return WritingGenerationResponse(
        prompt=result
    )

@router.post("/submit", response_model=WritingSummaryResponse)
def submit_text(request: WritingUserRequest):
    result = writing_file.submit_response(request.username, request.user_response)

    return WritingSummaryResponse(
        detailed_correction=result[0],
        summarised_correction=result[1]
    )

