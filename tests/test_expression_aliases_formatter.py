"""Tests for expression_aliases_formatter module."""
import pytest
from crontab_lint.expression_aliases import Alias, AliasStore
from crontab_lint.expression_aliases_formatter import (
    format_alias,
    format_aliases,
    format_summary,
)


@pytest.fixture
def alias():
    return Alias(name="daily", expression="0 0 * * *", description="Once a day")


def test_format_alias_contains_name(alias):
    result = format_alias(alias)
    assert "daily" in result


def test_format_alias_contains_expression(alias):
    result = format_alias(alias)
    assert "0 0 * * *" in result


def test_format_alias_contains_description(alias):
    result = format_alias(alias)
    assert "Once a day" in result


def test_format_alias_with_index(alias):
    result = format_alias(alias, index=3)
    assert result.startswith("3.")


def test_format_alias_no_description_omits_description_line():
    a = Alias(name="x", expression="* * * * *")
    result = format_alias(a)
    assert "Description" not in result


def test_format_aliases_empty_returns_no_aliases_message():
    result = format_aliases([])
    assert "No aliases" in result


def test_format_aliases_lists_all():
    aliases = [
        Alias(name="a", expression="* * * * *"),
        Alias(name="b", expression="0 0 * * *"),
    ]
    result = format_aliases(aliases)
    assert "a" in result
    assert "b" in result


def test_format_aliases_numbered():
    aliases = [Alias(name="x", expression="0 0 * * *")]
    result = format_aliases(aliases)
    assert "1." in result


def test_format_summary_single():
    store = AliasStore()
    store.add(Alias(name="only", expression="0 0 * * *"))
    result = format_summary(store)
    assert "1 alias" in result


def test_format_summary_plural():
    store = AliasStore()
    store.add(Alias(name="a", expression="* * * * *"))
    store.add(Alias(name="b", expression="0 0 * * *"))
    result = format_summary(store)
    assert "2 aliases" in result


def test_format_summary_empty():
    store = AliasStore()
    result = format_summary(store)
    assert "0" in result
