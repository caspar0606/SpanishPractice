"""Every tracked tense and grammar point has a learner-facing lesson."""

from src.domain.enums import Grammar, Tenses, tracked_members
from src.infrastructure.persistence.json_content import JsonContentRepository


def test_every_tracked_concept_has_a_lesson():
    repo = JsonContentRepository()
    keys = {lesson.key for lesson in repo.lessons()}
    for member in tracked_members(Tenses):
        assert member.value in keys, member.value
    for member in tracked_members(Grammar):
        assert member.value in keys, member.value


def test_search_finds_present_tense_from_english():
    repo = JsonContentRepository()
    hits = repo.search_lessons("when do I use the present tense")
    assert hits
    assert hits[0].key == "presente_de_indicativo"


def test_por_para_search():
    repo = JsonContentRepository()
    hits = repo.search_lessons("para or por")
    assert any(item.key == "por_para_usage" for item in hits)


def test_tense_tables_include_common_irregulars():
    repo = JsonContentRepository()
    present = repo.lesson("presente_de_indicativo")
    preterite = repo.lesson("preterito_perfecto_simple")
    assert present is not None and preterite is not None
    assert present.table["hablar"]["yo"] == "hablo"
    assert present.table["ser"]["yo"] == "soy"
    assert present.table["tener"]["yo"] == "tengo"
    assert present.table["hacer"]["yo"] == "hago"
    assert preterite.table["ser"]["yo"] == "fui"
    assert preterite.table["ir"]["yo"] == "fui"
    assert preterite.table["tener"]["yo"] == "tuve"
    assert preterite.table["hacer"]["él/ella"] == "hizo"


def test_search_finds_preterite_from_an_irregular_form():
    repo = JsonContentRepository()
    hits = repo.search_lessons("tuve")
    assert hits
    assert hits[0].key == "preterito_perfecto_simple"
