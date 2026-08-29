"""Light review scheduling for vocab. Not a full SRS."""

from datetime import datetime, timedelta

from src.domain.enums import VocabStatus
from src.domain.models.vocab import VocabEntry

REVIEW_BATCH = 5


def is_due(entry: VocabEntry, now: datetime | None = None) -> bool:
    if entry.status is VocabStatus.IGNORED:
        return False
    if entry.status is VocabStatus.KNOWN:
        return False
    now = now or datetime.now()
    if entry.next_review is None:
        return True
    return entry.next_review <= now


def due_entries(entries: list[VocabEntry], now: datetime | None = None) -> list[VocabEntry]:
    now = now or datetime.now()
    due = [entry for entry in entries if is_due(entry, now)]
    due.sort(key=lambda item: (not item.starred, item.next_review or now, item.lemma))
    return due


def schedule_after(entry: VocabEntry, correct: bool, now: datetime | None = None) -> VocabEntry:
    now = now or datetime.now()
    entry.times_seen += 1
    if correct:
        entry.times_correct += 1
        if entry.times_correct >= 3:
            entry.status = VocabStatus.KNOWN
            entry.next_review = now + timedelta(days=14)
        else:
            entry.status = VocabStatus.LEARNING
            entry.next_review = now + timedelta(days=2)
    else:
        entry.status = VocabStatus.LEARNING
        entry.next_review = now + timedelta(hours=12)
    return entry


def normalise_lemma(raw: str) -> str:
    return " ".join((raw or "").strip().lower().split())
