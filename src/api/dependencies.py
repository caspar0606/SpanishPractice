import os
import secrets

from fastapi import Header, HTTPException, status

ACCESS_KEY_HEADER = "X-Access-Key"


def _configured_access_key() -> str:
    key = os.getenv("ACCESS_KEY")
    if not key:
        # Fail closed. If the key is unset, an absent header would otherwise compare
        # equal to it and the check would silently become a no-op.
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Server is missing its ACCESS_KEY configuration.",
        )
    return key


def require_access_key(x_access_key: str | None = Header(default=None)) -> None:
    """Reject any request that does not carry the shared access code.

    Guards every endpoint that reads or writes user state, or that spends money by
    calling the model. Login is exempt because that is where the code is supplied.
    """
    expected = _configured_access_key()

    if x_access_key is None or not secrets.compare_digest(x_access_key, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid access code.",
        )
