"""Browse tense tables and grammar notes, and pick related lessons after an exercise."""

from src.application import container
from src.domain.enums import Grammar, Tenses, is_category_sentinel
from src.domain.models.lesson import Lesson
from src.domain.models.progress import Progress
from src.domain.rules.labels import label_for
from src.domain.rules.score import calculate_score


def index() -> list[dict]:
    items = []
    for lesson in container.content().lessons():
        items.append(
            {
                "key": lesson.key,
                "axis": lesson.axis,
                "title_en": lesson.title_en,
                "summary": lesson.summary(),
            },
        )
    items.sort(key=lambda row: (0 if row["axis"] == "tense" else 1, row["title_en"]))
    return items


def get(key: str) -> Lesson:
    lesson = container.content().lesson(key)
    if lesson is None:
        raise ValueError(f"No lesson for '{key}'")
    return lesson


def cards_for_score(score: Progress | None, limit: int = 2) -> list[dict]:
    """The 1–2 concepts with the most errors on this attempt."""
    if score is None:
        return []
    ranked: list[tuple[float, str]] = []
    for member, stats in {**score.tenses, **score.grammar}.items():
        if is_category_sentinel(member) or stats.total_attempts <= 0:
            continue
        accuracy = calculate_score(stats)
        errors = max(0.0, float(stats.total_attempts) - float(stats.correct_attempts))
        if errors <= 0 and accuracy >= 99:
            continue
        ranked.append((errors + (100 - accuracy) / 100, member.value))
    ranked.sort(reverse=True)
    cards = []
    seen: set[str] = set()
    for _, key in ranked:
        if key in seen:
            continue
        lesson = container.content().lesson(key)
        if lesson is None:
            continue
        seen.add(key)
        cards.append(card_dict(lesson))
        if len(cards) >= limit:
            break
    return cards


def related_for_user(username: str) -> list[dict]:
    user = container.users().load(username)
    if user is None or not user.exercise_history:
        return []
    return cards_for_score(user.exercise_history[-1].score)


def recent_error_keys(username: str) -> list[str]:
    user = container.users().load(username)
    if user is None or not user.exercise_history:
        return []
    score = user.exercise_history[-1].score
    return [card["key"] for card in cards_for_score(score, limit=4)]


def card_dict(lesson: Lesson) -> dict:
    return {
        "key": lesson.key,
        "axis": lesson.axis,
        "title_en": lesson.title_en,
        "summary": lesson.summary(),
    }


def label_for_key(key: str) -> str:
    for enum_cls in (Tenses, Grammar):
        try:
            return label_for(enum_cls(key))
        except ValueError:
            continue
    return key.replace("_", " ")
