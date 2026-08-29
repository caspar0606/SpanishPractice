"""Reads the curated content bank from `content/*.json`.

Files are small and change only on deploy, so they are cached after first read.
"""

import json
import os
import re
from functools import lru_cache
from pathlib import Path

from src.domain.models.lesson import Lesson

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


@lru_cache(maxsize=None)
def _load_lessons() -> tuple[Lesson, ...]:
    lessons: list[Lesson] = []
    for folder in ("tenses", "grammar"):
        directory = CONTENT_DIR / folder
        if not directory.is_dir():
            continue
        for path in sorted(directory.glob("*.json")):
            with path.open("r", encoding="utf-8") as f:
                lessons.append(Lesson.model_validate(json.load(f)))
    return tuple(lessons)


_TOKEN = re.compile(r"[a-záéíóúüñ0-9]{3,}", re.IGNORECASE)


def _tokens(text: str) -> set[str]:
    return {match.group(0).lower() for match in _TOKEN.finditer(text or "")}


class JsonContentRepository:
    def placement_bank(self) -> dict:
        return _read("placement.json")

    def curriculum(self) -> dict:
        return _read("curriculum.json")

    def lessons(self) -> list[Lesson]:
        return list(_load_lessons())

    def lesson(self, key: str) -> Lesson | None:
        for item in _load_lessons():
            if item.key == key:
                return item
        return None

    def search_lessons(self, query: str, limit: int = 4) -> list[Lesson]:
        needles = _tokens(query)
        if not needles:
            return []
        ranked: list[tuple[int, Lesson]] = []
        for item in _load_lessons():
            haystack = _tokens(item.searchable_text())
            score = len(needles & haystack)
            if item.key.replace("_", " ") in query.lower() or item.key in query.lower():
                score += 3
            if item.title_en.lower() in query.lower():
                score += 2
            if score:
                ranked.append((score, item))
        ranked.sort(key=lambda pair: (-pair[0], pair[1].title_en))
        return [item for _, item in ranked[:limit]]
