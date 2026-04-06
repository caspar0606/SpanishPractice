from fastapi import APIRouter

from src.application import exercise_selection as selection_file
from src.api.schemas.exercise import ExerciseRequest, ExerciseResponse

router = APIRouter()

@router.post("/generate", response_model=ExerciseResponse)
def generate_reading_text(request: ExerciseRequest):
    result = selection_file.generate_exercise(request.username, request.type, request.difficulty, 
                                              request.style, request.preferences)

    return ExerciseResponse(
        exercise=result
    )