"""Parse Merriam-Webster Spanish–English JSON into a learner-facing lookup."""

import re

from src.domain.models.dictionary import DictionaryEntry, DictionaryLookup

_MARKUP = re.compile(r"\{([^}]*)\}")


def strip_markup(text: str) -> str:
    """Turn MW tokens such as {bc} and {sx|casa||} into plain text."""

    def replacer(match: re.Match[str]) -> str:
        inner = match.group(1)
        parts = inner.split("|")
        if len(parts) >= 2 and parts[1]:
            return parts[1]
        return ""

    cleaned = _MARKUP.sub(replacer, text or "")
    return re.sub(r"\s+", " ", cleaned).strip(" :;,")


def parse_response(query: str, payload) -> DictionaryLookup:
    if isinstance(payload, str):
        raise ValueError(payload.strip() or "Dictionary lookup failed")
    if not isinstance(payload, list) or not payload:
        return DictionaryLookup(query=query, found=False)
    if all(isinstance(item, str) for item in payload):
        suggestions = [item.strip() for item in payload if isinstance(item, str) and item.strip()]
        return DictionaryLookup(query=query, found=False, suggestions=suggestions[:8])

    spanish = [item for item in payload if isinstance(item, dict) and _lang(item) == "es"]
    chosen = spanish or [item for item in payload if isinstance(item, dict)]
    entries: list[DictionaryEntry] = []
    for item in chosen[:3]:
        entry = _entry_from(item)
        if entry.glosses:
            entries.append(entry)
    return DictionaryLookup(query=query, found=bool(entries), entries=entries)


def _lang(item: dict) -> str:
    meta = item.get("meta") or {}
    return str(meta.get("lang") or "").lower()


def _entry_from(item: dict) -> DictionaryEntry:
    headword = strip_markup(str((item.get("hwi") or {}).get("hw") or item.get("meta", {}).get("id") or ""))
    pos = str(item.get("fl") or "").strip()
    glosses = [strip_markup(g) for g in (item.get("shortdef") or []) if str(g).strip()]
    glosses = [g for g in glosses if g][:4]
    return DictionaryEntry(headword=headword, part_of_speech=pos, glosses=glosses)
