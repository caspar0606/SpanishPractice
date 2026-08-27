"""Reads the curated content bank from `content/*.json`.

Files are small and change only on deploy, so they are cached after first read.
"""

import json
import os
from functools import lru_cache
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[3]


def _content_dir() -> Path:
    raw = os.getenv("CONTENT_DIR")
    if not raw:
        return _PROJECT_ROOT / "content"
    path = Path(raw)
    return path if path.is_absolute() else _PROJECT_ROOT / path


CONTENT_DIR = _content_dir()


@lru_cache(maxsize=None)
def _read(name: str) -> dict:
    path = CONTENT_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"Content file '{name}' is missing from {CONTENT_DIR}")
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError(f"Content file '{name}' must contain a JSON object")
    return data


class JsonContentRepository:
    def placement_bank(self) -> dict:
        return _read("placement.json")
