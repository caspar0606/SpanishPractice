"""Normalise a clicked token before it is sent to a dictionary."""

import unicodedata

MAX_LOOKUP_CHARS = 40
MAX_CANDIDATES = 5

# MW's Spanish API indexes many headwords without accents or ñ, and it does
# not list common irregular verb forms as stems. Map those forms to a lemma
# we can actually request.
_IRREGULAR_LEMMAS = {
    "estoy": "estar",
    "estás": "estar",
    "está": "estar",
    "estamos": "estar",
    "estáis": "estar",
    "están": "estar",
    "esté": "estar",
    "estés": "estar",
    "estemos": "estar",
    "estéis": "estar",
    "estén": "estar",
    "estaba": "estar",
    "estabas": "estar",
    "estábamos": "estar",
    "estado": "estar",
    "soy": "ser",
    "eres": "ser",
    "es": "ser",
    "somos": "ser",
    "sois": "ser",
    "son": "ser",
    "fui": "ser",
    "fue": "ser",
    "era": "ser",
    "eran": "ser",
    "sea": "ser",
    "sean": "ser",
    "sido": "ser",
    "he": "haber",
    "has": "haber",
    "ha": "haber",
    "hemos": "haber",
    "habéis": "haber",
    "han": "haber",
    "hay": "haber",
    "hubo": "haber",
    "había": "haber",
    "haya": "haber",
    "voy": "ir",
    "vas": "ir",
    "va": "ir",
    "vamos": "ir",
    "vais": "ir",
    "van": "ir",
    "iba": "ir",
    "vaya": "ir",
}


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


def fold_accents(text: str) -> str:
    """Strip diacritics so café → cafe and niño → nino."""
    decomposed = unicodedata.normalize("NFD", text or "")
    return "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn")


def display_headword(text: str) -> str:
    """Drop Merriam-Webster syllable breaks such as ca*sa."""
    return (text or "").replace("*", "").replace("·", "").strip()


def lemma_for(form: str) -> str | None:
    word = normalise_lookup(form)
    return _IRREGULAR_LEMMAS.get(word) or _IRREGULAR_LEMMAS.get(fold_accents(word))


def is_inflected_form(form: str, lemma: str) -> bool:
    """True when form is a regular gender/number variant of lemma."""
    form_key = fold_accents(normalise_lookup(form))
    lemma_key = fold_accents(normalise_lookup(lemma))
    if not form_key or not lemma_key or form_key == lemma_key:
        return False
    if form_key == lemma_key + "s":
        return True
    if lemma_key.endswith("z") and form_key == lemma_key[:-1] + "ces":
        return True
    if lemma_key.endswith("o"):
        stem = lemma_key[:-1]
        if form_key in {stem + "a", stem + "os", stem + "as"}:
            return True
    if lemma_key.endswith("a") and form_key == lemma_key + "s":
        return True
    return False


def lookup_candidates(word: str) -> list[str]:
    """Forms to try against a dictionary that is picky about accents and inflections."""
    primary = normalise_lookup(word)
    if not primary:
        return []
    ordered: list[str] = []
    seen: set[str] = set()

    def add(candidate: str) -> None:
        key = (candidate or "").strip()
        if not key or key in seen or len(ordered) >= MAX_CANDIDATES:
            return
        seen.add(key)
        ordered.append(key)

    add(primary)
    lemma = lemma_for(primary)
    if lemma:
        add(lemma)
        add(fold_accents(lemma))
    for inflected in _inflection_lemmas(primary):
        add(inflected)
        add(fold_accents(inflected))
    add(fold_accents(primary))
    return ordered


def _inflection_lemmas(word: str) -> list[str]:
    w = word
    lemmas: list[str] = []

    def add(candidate: str) -> None:
        if candidate and candidate != w and candidate not in lemmas:
            lemmas.append(candidate)

    if w.endswith("ces") and len(w) > 4:
        add(w[:-3] + "z")
    if w.endswith("s") and len(w) > 2:
        add(w[:-1])
    if w.endswith("os") and len(w) > 3:
        add(w[:-2] + "o")
    if w.endswith("as") and len(w) > 3:
        add(w[:-2] + "o")
        add(w[:-1])
    if w.endswith("a") and len(w) > 2:
        add(w[:-1] + "o")
    return lemmas
