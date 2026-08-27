from fastapi import APIRouter, HTTPException

from src.application.services import progress as progress_file
from src.api.schemas.progress import CurrentProgressRequest, CurrentProgressResponse


router = APIRouter()

@router.post("/generate", response_model=CurrentProgressResponse)
def return_progress(request: CurrentProgressRequest):
    try:
        result = progress_file.return_progress(request.username)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return CurrentProgressResponse(
        progress=result
    )
