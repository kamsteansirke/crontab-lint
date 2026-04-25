"""Tests for expression_aliases module."""
import json
import os
import pytest
from crontab_lint.expression_aliases import Alias, AliasStore


@pytest.fixture
def tmp_store(tmp_path):
    return str(tmp_path / "aliases.json")


def test_add_and_find():
    store = AliasStore()
    alias = Alias(name="daily", expression="0 0 * * *", description="Once a day")
    store.add(alias)
    found = store.find("daily")
    assert found is not None
    assert found.expression == "0 0 * * *"


def test_find_missing_returns_none():
    store = AliasStore()
    assert store.find("nope") is None


def test_remove_existing():
    store = AliasStore()
    store.add(Alias(name="hourly", expression="0 * * * *"))
    result = store.remove("hourly")
    assert result is True
    assert store.find("hourly") is None


def test_remove_missing_returns_false():
    store = AliasStore()
    assert store.remove("ghost") is False


def test_all_returns_all_aliases():
    store = AliasStore()
    store.add(Alias(name="a", expression="* * * * *"))
    store.add(Alias(name="b", expression="0 0 * * *"))
    assert len(store.all()) == 2


def test_add_overwrites_existing():
    store = AliasStore()
    store.add(Alias(name="daily", expression="0 0 * * *"))
    store.add(Alias(name="daily", expression="0 6 * * *"))
    assert store.find("daily").expression == "0 6 * * *"


def test_search_by_name():
    store = AliasStore()
    store.add(Alias(name="daily-backup", expression="0 2 * * *"))
    store.add(Alias(name="hourly", expression="0 * * * *"))
    results = store.search("daily")
    assert len(results) == 1
    assert results[0].name == "daily-backup"


def test_search_by_description():
    store = AliasStore()
    store.add(Alias(name="x", expression="0 0 * * *", description="midnight run"))
    store.add(Alias(name="y", expression="0 6 * * *", description="morning task"))
    results = store.search("midnight")
    assert len(results) == 1
    assert results[0].name == "x"


def test_save_and_load_roundtrip(tmp_store):
    store = AliasStore()
    store.add(Alias(name="weekly", expression="0 0 * * 0", description="Every Sunday"))
    store.save(tmp_store)
    loaded = AliasStore.load(tmp_store)
    found = loaded.find("weekly")
    assert found is not None
    assert found.expression == "0 0 * * 0"
    assert found.description == "Every Sunday"


def test_load_missing_file_returns_empty(tmp_store):
    store = AliasStore.load(tmp_store)
    assert store.all() == []
