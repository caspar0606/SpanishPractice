"""Spanish word lookup via the Merriam-Webster Spanish–English JSON API."""

import pytest
from fastapi.testclient import TestClient

from src.api.main import create_app
from src.application import container
from src.application.services import translate as translate_file
from src.domain.rules.dictionary import normalise_lookup
from src.infrastructure.dictionary.merriam import MerriamWebsterGateway
from src.infrastructure.dictionary.parse import parse_response, strip_markup


RODEO_PAYLOAD = [
    {
        "meta": {"id": "rodeo", "lang": "en", "src": "spanish"},
        "hwi": {"hw": "rodeo"},
        "fl": "noun",
        "shortdef": ["rodeo"],
    },
    {
        "meta": {"id": "rodeo", "lang": "es", "src": "spanish"},
        "hwi": {"hw": "rodeo"},
        "fl": "masculine noun",
        "shortdef": ["rodeo, roundup", "desvío : detour", "evasion"],
    },
]


def test_normalise_keeps_spanish_letters_and_drops_punctuation():
    assert normalise_lookup("¡Casa!") == "casa"
    assert normalise_lookup("niños") == "niños"


def test_strip_markup_expands_cross_references():
    assert strip_markup("{bc}{sx|desvío||} detour") == "desvío detour"


def test_parse_prefers_spanish_headword_entries():
    result = parse_response("rodeo", RODEO_PAYLOAD)
    assert result.found is True
    assert result.entries[0].part_of_speech == "masculine noun"
    assert "roundup" in result.entries[0].glosses[0]


def test_parse_suggestions_when_the_word_is_unknown():
    result = parse_response("casaa", ["casa", "caso", "caza"])
    assert result.found is False
    assert result.suggestions[0] == "casa"


def test_lookup_uses_the_dictionary_port(deps, fake_dictionary):
    result = translate_file.lookup_word("¡Casas!")
    assert result.found is True
    assert fake_dictionary.calls == ["casas"]
    assert result.entries[0].glosses[0] == "house"


def test_blank_lookup_is_rejected(deps):
    try:
        translate_file.lookup_word("...")
        assert False, "expected ValueError"
    except ValueError:
        pass


@pytest.fixture
def client(deps, monkeypatch, tmp_path):
    monkeypatch.setenv("ACCESS_KEY", "test-key")
    monkeypatch.setenv("USERDATA_DIR", str(tmp_path))
    app = create_app()
    container.configure(deps)
    with TestClient(app) as c:
        yield c


def test_translate_route(client):
    res = client.get("/translate/word", params={"q": "casa"})
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["found"] is True
    assert body["entries"][0]["glosses"]


def test_missing_key_explains_how_to_configure():
    gateway = MerriamWebsterGateway(api_key="")
    try:
        gateway.lookup("casa")
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "MERRIAM_WEBSTER_API_KEY" in str(exc)
