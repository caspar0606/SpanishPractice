"""On-disk cache for TTS clips. Audio is never stored on the user JSON."""

import hashlib
import os
from pathlib import Path

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


def path_for(clip_id: str) -> Path:
    return _audio_dir() / f"{clip_id}.mp3"


def get(clip_id: str) -> Path | None:
    path = path_for(clip_id)
    return path if path.is_file() else None


def put(clip_id: str, data: bytes) -> Path:
    path = path_for(clip_id)
    path.write_bytes(data)
    return path
