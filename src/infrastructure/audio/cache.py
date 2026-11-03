"""On-disk cache for TTS clips. Audio is never stored on the user JSON."""

import hashlib
import os
import re
from pathlib import Path

_CLIP_ID = re.compile(r"^[a-zA-Z0-9_-]{1,64}$")

_PROJECT_ROOT = Path(__file__).resolve().parents[3]


def _audio_dir() -> Path:
    raw = os.getenv("USERDATA_DIR")
    root = Path(raw) if raw else _PROJECT_ROOT / "userdata"
    if not root.is_absolute():
        root = _PROJECT_ROOT / root
    path = root / "audio"
    path.mkdir(parents=True, exist_ok=True)
    return path


def clip_id_for(text: str, voice: str) -> str:
    digest = hashlib.sha256(f"{voice}\n{text}".encode("utf-8")).hexdigest()
    return digest[:20]


def _safe_clip_id(clip_id: str) -> str | None:
    if not clip_id or not _CLIP_ID.fullmatch(clip_id):
        return None
    return clip_id


def path_for(clip_id: str) -> Path:
    safe = _safe_clip_id(clip_id)
    if safe is None:
        raise ValueError("Invalid audio clip id")
    return _audio_dir() / f"{safe}.mp3"


def get(clip_id: str) -> Path | None:
    if not _safe_clip_id(clip_id):
        return None
    path = path_for(clip_id)
    return path if path.is_file() else None


def put(clip_id: str, data: bytes) -> Path:
    path = path_for(clip_id)
    path.write_bytes(data)
    return path
