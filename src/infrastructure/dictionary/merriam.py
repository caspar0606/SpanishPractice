"""Merriam-Webster Spanish–English Dictionary API adapter."""

from urllib.parse import quote

import httpx

from src.domain.models.dictionary import DictionaryLookup
from src.infrastructure.config.config import MERRIAM_WEBSTER_API_KEY
from src.infrastructure.dictionary.parse import parse_response

_ENDPOINT = "https://www.dictionaryapi.com/api/v3/references/spanish/json/{word}"


class MerriamWebsterGateway:
    def __init__(self, api_key: str | None = None, client: httpx.Client | None = None) -> None:
        self._api_key = (api_key if api_key is not None else MERRIAM_WEBSTER_API_KEY) or ""
        self._api_key = self._api_key.strip().strip("'").strip('"')
        self._client = client
        self._cache: dict[str, DictionaryLookup] = {}

    def lookup(self, word: str) -> DictionaryLookup:
        key = (word or "").strip()
        if not key:
            raise ValueError("Pick a Spanish word first")
        if key in self._cache:
            return self._cache[key]
        if not self._api_key:
            raise ValueError(
                "Dictionary isn't configured. Set MERRIAM_WEBSTER_API_KEY to a "
                "Spanish-English Dictionary key from dictionaryapi.com.",
            )
        payload = self._fetch(key)
        result = parse_response(key, payload)
        self._cache[key] = result
        return result

    def _fetch(self, word: str):
        url = _ENDPOINT.format(word=quote(word, safe=""))
        client = self._client or httpx.Client(timeout=8.0)
        owns = self._client is None
        try:
            response = client.get(url, params={"key": self._api_key})
        except httpx.HTTPError as exc:
            raise ValueError("Couldn't reach the dictionary just now. Try again in a moment.") from exc
        finally:
            if owns:
                client.close()
        if response.status_code == 401 or response.status_code == 403:
            raise ValueError("The dictionary key was rejected. Check MERRIAM_WEBSTER_API_KEY.")
        if response.status_code >= 400:
            raise ValueError("The dictionary didn't return that word.")
        try:
            return response.json()
        except ValueError as exc:
            raise ValueError("The dictionary sent an unexpected response.") from exc
