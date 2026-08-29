"""Normalise a clicked token before it is sent to a dictionary."""

import unicodedata

MAX_LOOKUP_CHARS = 40


def normalise_lookup(raw: str) -> str:
    """Keep the first run of letters, including Spanish accents."""
    started = False
    chars: list[str] = []
    for ch in raw or "":
        if unicodedata.category(ch).startswith("L"):
            started = True
            chars.append(ch)
            if len(chars) >= MAX_LOOKUP_CHARS:
                break
            continue
        if started:
            break
    return "".join(chars).casefold()
