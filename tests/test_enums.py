"""Category sentinels are the enum members that name their own category.

Tenses.TENSES, Grammar.GRAMMAR and Topics.TOPICS exist so user files saved before they
were excluded still validate. They are not areas a learner can practise, so every
user-facing path has to be able to tell them apart from a real area.
"""

import pytest

from src.domain.enums import (
    Grammar,
    Tenses,
    Topics,
    is_category_sentinel,
    practice_members,
)
from tests.conftest import FOCUS_CATEGORIES


@pytest.mark.parametrize("sentinel", [Tenses.TENSES, Grammar.GRAMMAR, Topics.TOPICS])
def test_category_members_are_sentinels(sentinel):
    assert is_category_sentinel(sentinel)


@pytest.mark.parametrize(
    "member", [Tenses.FUTURO_SIMPLE, Grammar.POR_PARA_USAGE, Topics.TRAVEL]
)
def test_real_areas_are_not_sentinels(member):
    assert not is_category_sentinel(member)


def test_non_members_are_not_sentinels():
    """The predicate is checked against enum members, never bare strings."""
    assert not is_category_sentinel("tenses")
    assert not is_category_sentinel(None)


@pytest.mark.parametrize("category, enum_cls", FOCUS_CATEGORIES)
def test_practice_members_excludes_exactly_one_sentinel(category, enum_cls):
    members = practice_members(enum_cls)

    assert len(members) == len(list(enum_cls)) - 1
    assert not any(is_category_sentinel(member) for member in members)
