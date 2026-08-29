"""Look up a Spanish or English word in the bilingual dictionary."""

from src.application import container
from src.domain.models.dictionary import DictionaryLookup
from src.domain.rules.dictionary import normalise_lookup


def lookup_word(raw: str) -> DictionaryLookup:
    word = normalise_lookup(raw)
    if not word:
        raise ValueError("Pick a word first")
    return container.dictionary().lookup(word)
