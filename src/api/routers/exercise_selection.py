from fastapi import APIRouter, HTTPException

from src.api.schemas.exercise import (
    ExerciseRequest,
    ExerciseResponse,
    RecommendRequest,
    RecommendResponse,
)
from src.application import exercise_selection as selection_file
from src.application.services import recommender as recommender_file

router = APIRouter()


@router.post("/generate", response_model=ExerciseResponse)
def generate_exercise_endpoint(request: ExerciseRequest):
    try:
        result = selection_file.generate_exercise(
            request.username,
            request.type,
            request.style,
            request.preferences,
            request.length,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return ExerciseResponse(exercise=result)


@router.post("/recommend", response_model=RecommendResponse)
def recommend_endpoint(request: RecommendRequest):
    try:
        cards = recommender_file.recommend(request.username)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return RecommendResponse(cards=cards)