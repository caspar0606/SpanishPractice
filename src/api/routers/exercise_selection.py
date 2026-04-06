from fastapi import APIRouter, HTTPException

from src.application import exercise_selection as selection_file
from src.api.schemas.exercise import ExerciseRequest, ExerciseResponse

router = APIRouter()


@router.post("/generate", response_model=ExerciseResponse)
def generate_exercise_endpoint(request: ExerciseRequest):
    try:
        result = selection_file.generate_exercise(
            request.username,
            request.type,
            request.difficulty,
            request.style,
            request.preferences,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return ExerciseResponse(exercise=result)