"""Look up a Spanish word for the click-to-translate popover."""

from src.application import container
from src.domain.models.dictionary import DictionaryLookup
from src.domain.rules.dictionary import normalise_lookup


def lookup_word(raw: str) -> DictionaryLookup:
    word = normalise_lookup(raw)
    if not word:
        raise ValueError("Pick a Spanish word first")
    return container.dictionary().lookup(word)
