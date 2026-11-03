"""Signed session tokens. The username lives in the token, not in the request body."""

import base64
import hashlib
import hmac
import json
import os
import time

MAX_AGE_SECONDS = 14 * 24 * 3600


def _b64encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def _b64decode(text: str) -> bytes:
    pad = "=" * (-len(text) % 4)
    return base64.urlsafe_b64decode(text + pad)


def _secret() -> bytes:
    raw = os.getenv("SESSION_SECRET") or os.getenv("ACCESS_KEY") or ""
    raw = raw.strip().strip("'").strip('"')
    if not raw:
        raise RuntimeError("SESSION_SECRET or ACCESS_KEY must be set to sign sessions")
    return raw.encode("utf-8")


def issue(username: str) -> str:
    payload = {"u": username, "exp": int(time.time()) + MAX_AGE_SECONDS}
    body = _b64encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    sig = hmac.new(_secret(), body.encode("ascii"), hashlib.sha256).digest()
    return f"{body}.{_b64encode(sig)}"


def verify(token: str | None) -> str | None:
    if not token or "." not in token:
        return None
    body, sig = token.split(".", 1)
    expected = hmac.new(_secret(), body.encode("ascii"), hashlib.sha256).digest()
    try:
        given = _b64decode(sig)
    except (ValueError, OSError):
        return None
    if not hmac.compare_digest(expected, given):
        return None
    try:
        payload = json.loads(_b64decode(body))
    except (ValueError, json.JSONDecodeError):
        return None
    if int(payload.get("exp") or 0) < time.time():
        return None
    username = payload.get("u")
    if not isinstance(username, str) or not username:
        return None
    return username
