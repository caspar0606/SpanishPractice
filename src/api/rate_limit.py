"""In-process sliding window. Enough for a single Railway web dyno."""

import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request

_hits: dict[tuple[str, str], deque[float]] = defaultdict(deque)


def enforce(key: str, bucket: str, limit: int, window_s: float = 60.0) -> None:
    now = time.monotonic()
    q = _hits[(bucket, key)]
    cutoff = now - window_s
    while q and q[0] < cutoff:
        q.popleft()
    if len(q) >= limit:
        raise HTTPException(
            status_code=429,
            detail="Too many requests. Wait a moment and try again.",
        )
    q.append(now)


def client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip() or "unknown"
    if request.client and request.client.host:
        return request.client.host
    return "unknown"
