"""Parse Merriam-Webster Spanish–English JSON into a learner-facing lookup."""

import re
import unicodedata

from src.domain.models.dictionary import DictionaryEntry, DictionaryLookup
from src.domain.rules.dictionary import (
    display_headword,
    fold_accents,
    is_inflected_form,
    lemma_for,
    normalise_lookup,
)

_MARKUP = re.compile(r"\{([^}]*)\}")
_LETTER_GLOSS = re.compile(
    r"letra del alfabeto|letter of the .{0,24}alphabet",
    re.I,
)
_PHRASE_MARK = re.compile(r"[\s-]")


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


def clean_gloss(text: str) -> str:
    """Prefer the translation after a synonym colon such as 'lindo : pretty'."""
    gloss = strip_markup(text).replace("*", "")
    gloss = re.sub(r"\s+", " ", gloss).strip(" :;,")
    if " : " in gloss:
        left, right = gloss.split(" : ", 1)
        if right.strip() and len(left.split()) <= 2:
            gloss = right.strip()
    return gloss


def parse_response(query: str, payload) -> DictionaryLookup:
    if isinstance(payload, str):
        raise ValueError(payload.strip() or "Dictionary lookup failed")
    if not isinstance(payload, list) or not payload:
        return DictionaryLookup(query=query, found=False)
    if all(isinstance(item, str) for item in payload):
        suggestions = [item.strip() for item in payload if isinstance(item, str) and item.strip()]
        return DictionaryLookup(query=query, found=False, suggestions=_unique(suggestions)[:8])

    items = [item for item in payload if isinstance(item, dict)]
    by_id = {
        str((item.get("meta") or {}).get("id")): item
        for item in items
        if (item.get("meta") or {}).get("id")
    }
    ranked = [(_relevance(item, query), item) for item in items]
    ranked = [(score, item) for score, item in ranked if score > 0]
    ranked.sort(key=lambda pair: pair[0], reverse=True)
    if not ranked:
        return DictionaryLookup(query=query, found=False)

    best = ranked[0][0]
    if best >= 100:
        cutoff = 93
    elif best >= 93:
        cutoff = 93
    elif best >= 92:
        cutoff = 92
    else:
        cutoff = 50
    chosen = [item for score, item in ranked if score >= cutoff][:4]
    q = normalise_lookup(query)
    feminine = q.endswith(("a", "as", "os", "es"))
    chosen.sort(
        key=lambda item: (
            0
            if feminine
            and _lang(item) == "es"
            and "adjective" in str(item.get("fl") or "").lower()
            else 1,
            -_relevance(item, query),
        )
    )

    entries: list[DictionaryEntry] = []
    for item in chosen:
        followed = _follow_xrs(item, by_id)
        extra = [followed] if followed else None
        entry = _entry_from(item, extra)
        if entry.glosses:
            entries.append(entry)
    return DictionaryLookup(query=query, found=bool(entries), entries=entries)


def _lang(item: dict) -> str:
    meta = item.get("meta") or {}
    return str(meta.get("lang") or "").lower()


def _weakness(item: dict) -> int:
    """Downrank abbreviations, prefixes, and letter-of-the-alphabet entries."""
    fl = str(item.get("fl") or "").lower()
    if "abbreviation" in fl or "prefix" in fl:
        return 25
    glosses = " ".join(str(g) for g in (item.get("shortdef") or []))
    if _LETTER_GLOSS.search(glosses):
        return 25
    return 0


def _raw_headword(item: dict) -> str:
    raw = str((item.get("hwi") or {}).get("hw") or item.get("meta", {}).get("id") or "")
    return display_headword(raw.split(":")[0])


def _headword_of(item: dict) -> str:
    return normalise_lookup(_raw_headword(item))


def _phrase_headword_key(item: dict) -> str:
    chars: list[str] = []
    started = False
    for ch in _raw_headword(item):
        if unicodedata.category(ch).startswith("L") or ch in "-'":
            started = True
            chars.append(ch.casefold())
            continue
        if ch.isspace() and started:
            chars.append(" ")
            continue
        if started:
            break
    return re.sub(r"\s+", " ", "".join(chars)).strip()


def _is_phrase_headword(item: dict) -> bool:
    return bool(_PHRASE_MARK.search(_raw_headword(item)))


def _alternate_headwords(item: dict) -> list[str]:
    found: list[str] = []
    for alt in item.get("ahws") or []:
        if not isinstance(alt, dict):
            continue
        word = normalise_lookup(display_headword(str(alt.get("hw") or "")))
        if word:
            found.append(word)
    return found


def _single_word_stems(item: dict) -> list[str]:
    stems = (item.get("meta") or {}).get("stems") or []
    found: list[str] = []
    for stem in stems:
        text = str(stem)
        if " " in text or "/" in text:
            continue
        word = normalise_lookup(display_headword(text))
        if word:
            found.append(word)
    return found


def _relevance(item: dict, query: str) -> int:
    q = normalise_lookup(query)
    if not q:
        return 0
    if _is_phrase_headword(item):
        phrase = _phrase_headword_key(item)
        compact = re.sub(r"[\s-]+", "", phrase)
        if phrase == q or compact == q:
            return max(1, 100 - _weakness(item))
        return 0
    hw = _headword_of(item)
    alternates = _alternate_headwords(item)
    stems = _single_word_stems(item)
    q_fold = fold_accents(q)
    hw_fold = fold_accents(hw)

    if hw == q or q in alternates:
        score = 100
    elif q in stems:
        score = 95
    elif is_inflected_form(q, hw) or any(is_inflected_form(q, alt) for alt in alternates):
        score = 93
    else:
        mapped = lemma_for(q)
        if mapped and fold_accents(mapped) == hw_fold:
            score = 92
        elif hw_fold == q_fold or any(fold_accents(alt) == q_fold for alt in alternates):
            score = 50
        elif any(fold_accents(stem) == q_fold for stem in stems):
            score = 50
        else:
            return 0
    return max(1, score - _weakness(item))


def _entry_from(item: dict, followed: list[dict] | None = None) -> DictionaryEntry:
    headword = display_headword(
        str((item.get("hwi") or {}).get("hw") or item.get("meta", {}).get("id") or "")
    )
    pos = str(item.get("fl") or "").strip()
    glosses = _glosses_from(item)
    if not glosses:
        for extra in followed or []:
            glosses.extend(_glosses_from(extra))
            if not pos:
                pos = str(extra.get("fl") or "").strip()
            if glosses:
                break
    glosses = _unique(glosses)[:4]
    lang = _lang(item)
    return DictionaryEntry(
        headword=headword,
        part_of_speech=pos,
        glosses=glosses,
        language=lang if lang in {"en", "es"} else "",
    )


def _glosses_from(item: dict) -> list[str]:
    glosses = [clean_gloss(g) for g in (item.get("shortdef") or []) if str(g).strip()]
    glosses = [g for g in glosses if g]
    if glosses:
        return glosses
    from_def = _glosses_from_def(item)
    if from_def:
        return from_def
    from_cxs = _glosses_from_cxs(item)
    return from_cxs


def _glosses_from_def(item: dict) -> list[str]:
    found: list[str] = []
    for block in item.get("def") or []:
        if isinstance(block, dict):
            _walk_sseq(block.get("sseq"), found)
    return found[:4]


def _walk_sseq(node, found: list[str]) -> None:
    if len(found) >= 4:
        return
    if isinstance(node, list):
        if len(node) >= 2 and node[0] == "sense" and isinstance(node[1], dict):
            texts: list[str] = []
            for pair in node[1].get("dt") or []:
                if isinstance(pair, list) and len(pair) >= 2 and pair[0] == "text":
                    texts.append(str(pair[1]))
            gloss = clean_gloss(" ".join(texts))
            if gloss:
                found.append(gloss)
            return
        for child in node:
            _walk_sseq(child, found)


def _glosses_from_cxs(item: dict) -> list[str]:
    chunks: list[str] = []
    for cx in item.get("cxs") or []:
        if not isinstance(cx, dict):
            continue
        label = str(cx.get("cxl") or "").strip()
        targets = [
            str(part.get("cxt") or "").strip()
            for part in (cx.get("cxtis") or [])
            if isinstance(part, dict) and part.get("cxt")
        ]
        if label and targets:
            chunks.append(f"{label} {' + '.join(targets)}")
        elif label:
            chunks.append(label)
        elif targets:
            chunks.extend(targets)
    if not chunks:
        return []
    return [re.sub(r"\s+", " ", " ".join(chunks)).strip()]


def _follow_xrs(item: dict, by_id: dict[str, dict]) -> dict:
    for group in item.get("xrs") or []:
        refs = group if isinstance(group, list) else [group]
        for ref in refs:
            if not isinstance(ref, dict):
                continue
            xref = str(ref.get("xref") or ref.get("xrt") or "")
            if xref in by_id and by_id[xref] is not item:
                return by_id[xref]
    return {}


def _unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        key = value.casefold()
        if not value or key in seen:
            continue
        seen.add(key)
        ordered.append(value)
    return ordered
