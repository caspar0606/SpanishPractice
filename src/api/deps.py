from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.api.rate_limit import client_ip, enforce
from src.infrastructure.auth import session

_bearer = HTTPBearer(auto_error=False)

COOKIE_NAME = "sp_session"


def current_username(
    request: Request,
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> str:
    token = creds.credentials if creds and creds.credentials else None
    if not token:
        token = request.cookies.get(COOKIE_NAME)
    username = session.verify(token)
    if not username:
        raise HTTPException(status_code=401, detail="Please sign in again")
    return username


def limited(bucket: str, max_hits: int, window_s: float = 60.0):
    """Require a session, then cap that user on this bucket."""

    def dep(username: str = Depends(current_username)) -> str:
        enforce(username, bucket, max_hits, window_s)
        return username

    return dep


def limit_ip(bucket: str, max_hits: int, window_s: float = 60.0):
    def dep(request: Request) -> None:
        enforce(client_ip(request), bucket, max_hits, window_s)

    return dep
