from fastapi import APIRouter, HTTPException, Request, Response, Depends

from src.api.deps import COOKIE_NAME, current_username, limit_ip
from src.application import user as user_file
from src.application.services import onboarding as onboarding_file
from src.api.schemas.user import UserRequest, UserResponse
from src.infrastructure.auth import session as session_tokens

router = APIRouter()


@router.post("/login", response_model=UserResponse, dependencies=[Depends(limit_ip("login", 20))])
def select_user(request: UserRequest, raw: Request, response: Response):
    try:
        result = user_file.select_user(request.username, request.key, request.new)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    if result is None:
        raise HTTPException(status_code=401, detail="Invalid username or access code")

    token = session_tokens.issue(result.name)
    response.set_cookie(
        COOKIE_NAME,
        token,
        httponly=True,
        secure=raw.url.scheme == "https",
        samesite="lax",
        max_age=session_tokens.MAX_AGE_SECONDS,
        path="/",
    )
    return UserResponse(
        username=result.name,
        token=token,
        step=onboarding_file.current_step(result),
    )


@router.post("/logout")
def logout(response: Response, username: str = Depends(current_username)):
    response.delete_cookie(COOKIE_NAME, path="/")
    return {"ok": True, "username": username}
