"""Bilingual word lookup via the Merriam-Webster Spanish–English JSON API."""

from urllib.parse import unquote

import httpx
import pytest
from fastapi.testclient import TestClient

from src.api.main import create_app
from src.application import container
from src.application.services import translate as translate_file
from src.domain.rules.dictionary import lookup_candidates, normalise_lookup
from src.infrastructure.dictionary.merriam import MerriamWebsterGateway
from src.infrastructure.dictionary.parse import clean_gloss, parse_response, strip_markup


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


def test_clean_gloss_keeps_english_side_of_synonym_colon():
    assert clean_gloss("lindo : pretty, lovely") == "pretty, lovely"
    assert clean_gloss("{bc}house") == "house"


def test_candidates_cover_accents_gender_and_irregulars():
    pequena = lookup_candidates("pequeña")
    assert "pequeña" in pequena
    assert "pequeño" in pequena
    assert "pequeno" in pequena
    assert "estar" in lookup_candidates("está")
    assert "casa" in lookup_candidates("casas")


def test_parse_keeps_both_languages_for_homographs():
    result = parse_response("rodeo", RODEO_PAYLOAD)
    assert result.found is True
    by_lang = {entry.language: entry for entry in result.entries}
    assert set(by_lang) == {"en", "es"}
    assert by_lang["es"].part_of_speech == "masculine noun"
    assert "roundup" in by_lang["es"].glosses[0]


def test_parse_returns_spanish_glosses_for_english_queries():
    payload = [
        {
            "meta": {"id": "casa", "lang": "es", "stems": ["casa"]},
            "hwi": {"hw": "casa"},
            "fl": "feminine noun",
            "shortdef": ["house"],
        },
        {
            "meta": {"id": "house:2", "lang": "en", "stems": ["house", "houses"]},
            "hwi": {"hw": "house"},
            "fl": "noun",
            "shortdef": ["home : casa", "cámara (del gobierno)"],
        },
    ]
    result = parse_response("house", payload)
    assert result.found is True
    assert result.entries[0].headword == "house"
    assert result.entries[0].language == "en"
    assert result.entries[0].glosses[0] == "casa"


def test_parse_keeps_english_colour_not_only_spanish_net():
    payload = [
        {
            "meta": {"id": "red:1", "lang": "en", "stems": ["red"]},
            "hwi": {"hw": "red"},
            "fl": "adjective",
            "shortdef": ["rojo, colorado"],
        },
        {
            "meta": {"id": "red", "lang": "es", "stems": ["red"]},
            "hwi": {"hw": "red"},
            "fl": "feminine noun",
            "shortdef": ["net, mesh"],
        },
    ]
    result = parse_response("red", payload)
    langs = {entry.language: entry for entry in result.entries}
    assert set(langs) == {"en", "es"}
    assert langs["en"].glosses[0].startswith("rojo")
    assert langs["es"].glosses[0].startswith("net")


def test_parse_prefers_pronoun_i_over_letter_names():
    payload = [
        {
            "meta": {"id": "i", "lang": "en"},
            "hwi": {"hw": "i"},
            "fl": "noun",
            "shortdef": ["novena letra del alfabeto inglés"],
        },
        {
            "meta": {"id": "I", "lang": "en"},
            "hwi": {"hw": "I"},
            "fl": "pronoun",
            "shortdef": ["yo"],
        },
        {
            "meta": {"id": "i", "lang": "es"},
            "hwi": {"hw": "i"},
            "fl": "feminine noun",
            "shortdef": ["tenth letter of the Spanish alphabet"],
        },
    ]
    result = parse_response("I", payload)
    assert result.entries[0].part_of_speech == "pronoun"
    assert result.entries[0].glosses == ["yo"]


def test_parse_drops_english_compound_neighbours():
    payload = [
        {
            "meta": {"id": "red:1", "lang": "en", "stems": ["red"]},
            "hwi": {"hw": "red"},
            "fl": "adjective",
            "shortdef": ["rojo, colorado"],
        },
        {
            "meta": {"id": "red blood cell", "lang": "en", "stems": ["red", "red blood cell"]},
            "hwi": {"hw": "red blood cell"},
            "fl": "noun",
            "shortdef": ["glóbulo rojo"],
        },
        {
            "meta": {"id": "he-man", "lang": "en", "stems": ["he", "he-man"]},
            "hwi": {"hw": "he-man"},
            "fl": "noun",
            "shortdef": ["macho, machote"],
        },
    ]
    red = parse_response("red", payload)
    assert [entry.headword for entry in red.entries] == ["red"]
    he = parse_response("he", payload)
    assert [entry.headword for entry in he.entries] == []


def test_parse_suggestions_when_the_word_is_unknown():
    result = parse_response("casaa", ["casa", "caso", "caza"])
    assert result.found is False
    assert result.suggestions[0] == "casa"


def test_parse_drops_phrase_only_neighbours():
    payload = [
        {
            "meta": {"id": "casa", "lang": "es", "stems": ["casa", "casa de cambio"]},
            "hwi": {"hw": "ca*sa"},
            "fl": "feminine noun",
            "shortdef": ["house", "hogar : home"],
        },
        {
            "meta": {"id": "amo", "lang": "es", "stems": ["amo", "ama de casa"]},
            "hwi": {"hw": "amo"},
            "fl": "noun",
            "shortdef": ["master mistress"],
        },
        {
            "meta": {"id": "gasto", "lang": "es", "stems": ["gasto", "gastos de la casa"]},
            "hwi": {"hw": "gasto"},
            "fl": "masculine noun",
            "shortdef": ["expense"],
        },
    ]
    result = parse_response("casa", payload)
    assert [entry.headword for entry in result.entries] == ["casa"]
    assert result.entries[0].glosses[0] == "house"
    assert result.entries[0].glosses[1] == "home"


def test_parse_keeps_gendered_adjective_not_a_greeting_phrase():
    payload = [
        {
            "meta": {
                "id": "bueno:1",
                "lang": "es",
                "stems": ["bueno", "buena", "buenas tardes"],
            },
            "hwi": {"hw": "bueno"},
            "ahws": [{"hw": "buena", "hwc": "-na"}],
            "fl": "adjective",
            "shortdef": ["good"],
        },
        {
            "meta": {"id": "tarde:2", "lang": "es", "stems": ["tarde", "¡buenas tardes!"]},
            "hwi": {"hw": "tarde"},
            "fl": "feminine noun",
            "shortdef": ["afternoon"],
        },
    ]
    result = parse_response("buenas", payload)
    assert result.entries[0].headword == "bueno"
    assert result.entries[0].glosses == ["good"]


def test_parse_keeps_adjective_alongside_an_exact_noun_homograph():
    payload = [
        {
            "meta": {"id": "blanca", "lang": "es", "stems": ["blanca"]},
            "hwi": {"hw": "blanca"},
            "fl": "feminine noun",
            "shortdef": ["half note (in music)"],
        },
        {
            "meta": {"id": "blanco:1", "lang": "es", "stems": ["blanco", "blanca"]},
            "hwi": {"hw": "blanco"},
            "ahws": [{"hw": "blanca"}],
            "fl": "adjective",
            "shortdef": ["white"],
        },
    ]
    result = parse_response("blanca", payload)
    assert [entry.part_of_speech for entry in result.entries] == ["adjective", "feminine noun"]
    assert result.entries[0].glosses == ["white"]


def test_parse_follows_cross_references_when_shortdef_is_empty():
    payload = [
        {
            "meta": {"id": "hay", "lang": "es", "stems": ["hay"]},
            "hwi": {"hw": "hay"},
            "shortdef": [],
            "xrs": [[{"xrt": "haber:1", "xref": "haber:1"}]],
        },
        {
            "meta": {"id": "haber:1", "lang": "es", "stems": ["haber", "hay que"]},
            "hwi": {"hw": "haber"},
            "fl": "auxiliary verb",
            "shortdef": ["have, has", "there is, there are"],
        },
    ]
    result = parse_response("hay", payload)
    assert result.found is True
    assert [entry.headword for entry in result.entries] == ["hay"]
    assert "there is, there are" in result.entries[0].glosses


def test_parse_renders_contractions():
    payload = [
        {
            "meta": {"id": "del", "lang": "es", "stems": ["del"]},
            "hwi": {"hw": "del"},
            "shortdef": [],
            "cxs": [
                {"cxl": "contraction of", "cxtis": [{"cxt": "de"}]},
                {"cxl": "and", "cxtis": [{"cxt": "el"}]},
            ],
        }
    ]
    result = parse_response("del", payload)
    assert result.found is True
    assert "de" in result.entries[0].glosses[0]
    assert "el" in result.entries[0].glosses[0]


def test_gateway_retries_lemma_when_inflected_form_is_unknown():
    calls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        word = unquote(request.url.path.rsplit("/", 1)[-1])
        calls.append(word)
        if word == "casas":
            return httpx.Response(200, json=["casa", "caso"])
        if word == "casa":
            return httpx.Response(
                200,
                json=[
                    {
                        "meta": {"id": "casa", "lang": "es", "stems": ["casa"]},
                        "hwi": {"hw": "casa"},
                        "fl": "feminine noun",
                        "shortdef": ["house"],
                    }
                ],
            )
        return httpx.Response(200, json=[])

    client = httpx.Client(transport=httpx.MockTransport(handler))
    gateway = MerriamWebsterGateway(api_key="test-key", client=client)
    result = gateway.lookup("casas")
    assert result.found is True
    assert result.entries[0].glosses == ["house"]
    assert calls[0] == "casas"
    assert "casa" in calls


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
