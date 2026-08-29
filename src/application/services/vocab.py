"""Per-user vocab: extract after genuine work, star/ignore, light review."""

from datetime import datetime

from src.application import container
from src.domain.enums import AgentNames, Topics, VocabStatus
from src.domain.models.llm import agent_request
from src.domain.models.user import User
from src.domain.models.vocab import VocabEntry
from src.domain.rules import vocab as vocab_rules
from src.infrastructure.llm.contracts.learn import VocabExtraction
from src.infrastructure.llm.prompts.vocab import VOCAB_PROMPT_CONFIG


def list_entries(username: str) -> list[VocabEntry]:
    user = _load(username)
    return list(user.vocab)


def due(username: str) -> list[VocabEntry]:
    user = _load(username)
    return vocab_rules.due_entries(user.vocab)[: vocab_rules.REVIEW_BATCH]


def mark(username: str, lemma: str, status: VocabStatus | None = None, starred: bool | None = None) -> VocabEntry:
    user = _load(username)
    key = vocab_rules.normalise_lemma(lemma)
    entry = _find(user, key)
    if entry is None:
        raise ValueError(f"No vocab item '{lemma}'")
    if status is not None:
        entry.status = status
        if status is VocabStatus.IGNORED:
            entry.next_review = None
    if starred is not None:
        entry.starred = starred
    container.users().save(user)
    return entry


def record_review(username: str, results: list[dict]) -> list[VocabEntry]:
    """results: [{lemma, correct: bool}, ...]"""
    user = _load(username)
    now = datetime.now()
    updated: list[VocabEntry] = []
    for row in results:
        key = vocab_rules.normalise_lemma(str(row.get("lemma", "")))
        entry = _find(user, key)
        if entry is None:
            continue
        vocab_rules.schedule_after(entry, bool(row.get("correct")), now)
        updated.append(entry)
    container.users().save(user)
    return updated


def harvest(username: str, text: str) -> None:
    """Best-effort extract after a genuine attempt. Failures must not break submit."""
    cleaned = (text or "").strip()
    if len(cleaned.split()) < 8:
        return
    try:
        user = _load(username)
        ignored = [entry.lemma for entry in user.vocab if entry.status is VocabStatus.IGNORED]
        request = agent_request(
            name=AgentNames.VOCAB_EXTRACTOR,
            system_prompt=VOCAB_PROMPT_CONFIG[AgentNames.VOCAB_EXTRACTOR],
            stimulus={"ignore": ignored} if ignored else None,
            input=cleaned,
            schema=VocabExtraction,
        )
        extracted = container.llm().structured(request, VocabExtraction)
    except Exception:
        return
    _merge(user, extracted)
    container.users().save(user)


def _merge(user: User, extracted: VocabExtraction) -> None:
    by_lemma = {entry.lemma: entry for entry in user.vocab}
    for item in extracted.items[:10]:
        lemma = vocab_rules.normalise_lemma(item.lemma)
        if not lemma:
            continue
        existing = by_lemma.get(lemma)
        if existing is not None:
            if existing.status is VocabStatus.IGNORED:
                continue
            existing.times_seen += 1
            if not existing.gloss_en:
                existing.gloss_en = item.gloss_en
            continue
        topic = None
        if item.topic:
            try:
                topic = Topics(item.topic)
            except ValueError:
                topic = None
        entry = VocabEntry(lemma=lemma, gloss_en=item.gloss_en or lemma, topic=topic)
        user.vocab.append(entry)
        by_lemma[lemma] = entry


def _find(user: User, lemma: str) -> VocabEntry | None:
    for entry in user.vocab:
        if entry.lemma == lemma:
            return entry
    return None


def _load(username: str) -> User:
    user = container.users().load(username)
    if user is None:
        raise ValueError(f"User '{username}' not found")
    return user
