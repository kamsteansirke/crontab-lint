import pytest
from pathlib import Path
from crontab_lint.watchlist import (
    Watchlist, WatchedExpression, add, remove, find, all_entries, save, load
)


@pytest.fixture
def wl():
    return Watchlist()


@pytest.fixture
def tmp_file(tmp_path):
    return tmp_path / "watchlist.json"


def test_add_entry(wl):
    e = add(wl, "0 * * * *", "hourly")
    assert e.expression == "0 * * * *"
    assert e.label == "hourly"
    assert len(wl.entries) == 1


def test_add_with_notes_and_tags(wl):
    e = add(wl, "* * * * *", "every-min", notes="runs often", tags=["prod"])
    assert e.notes == "runs often"
    assert "prod" in e.tags


def test_find_existing(wl):
    add(wl, "0 0 * * *", "daily")
    result = find(wl, "daily")
    assert result is not None
    assert result.expression == "0 0 * * *"


def test_find_missing_returns_none(wl):
    assert find(wl, "nonexistent") is None


def test_find_case_insensitive(wl):
    add(wl, "0 0 * * *", "Daily")
    assert find(wl, "daily") is not None


def test_remove_existing(wl):
    add(wl, "0 0 * * *", "daily")
    removed = remove(wl, "daily")
    assert removed is True
    assert len(wl.entries) == 0


def test_remove_missing(wl):
    removed = remove(wl, "ghost")
    assert removed is False


def test_all_entries(wl):
    add(wl, "0 * * * *", "a")
    add(wl, "* * * * *", "b")
    assert len(all_entries(wl)) == 2


def test_save_and_load_roundtrip(wl, tmp_file):
    add(wl, "0 0 * * *", "daily", notes="midnight", tags=["prod"])
    save(wl, tmp_file)
    loaded = load(tmp_file)
    assert len(loaded.entries) == 1
    assert loaded.entries[0].label == "daily"
    assert loaded.entries[0].tags == ["prod"]


def test_load_missing_file(tmp_file):
    wl = load(tmp_file)
    assert wl.entries == []
