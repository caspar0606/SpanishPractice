from fastapi import APIRouter, Depends

from src.api.deps import current_username, limited
from src.api.errors import http_from_value_error
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
def generate_exercise_endpoint(
    request: ExerciseRequest,
    username: str = Depends(limited("exercise_generate", 20)),
):
    try:
        result = selection_file.generate_exercise(
            username,
            request.type,
            request.style,
            request.preferences,
            request.length,
            replace=request.replace,
        )
    except ValueError as e:
        raise http_from_value_error(e) from e

    return ExerciseResponse(exercise=result)


@router.post("/recommend", response_model=RecommendResponse)
def recommend_endpoint(request: RecommendRequest, username: str = Depends(current_username)):
    try:
        plan = recommender_file.recommend(username, request.day, request.tz_offset_minutes)
    except ValueError as e:
        raise http_from_value_error(e) from e

    return RecommendResponse(
        remaining=plan.remaining,
        complete=plan.complete,
        daily=plan.daily,
        extras=plan.extras,
        cards=recommender_file.startable_cards(plan),
    )
