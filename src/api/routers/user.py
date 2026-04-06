from fastapi import APIRouter, HTTPException

from src.application import user as user_file
from src.api.schemas.user import UserRequest, UserResponse

router = APIRouter()


@router.post("/login", response_model=UserResponse)
def select_user(request: UserRequest):
    try:
        result = user_file.select_user(request.username, request.key, request.new)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    if result is None:
        raise HTTPException(status_code=401, detail="Invalid access code")

    return UserResponse(user=result)