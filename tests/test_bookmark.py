"""Tests for bookmark module and CLI."""
import json
import pytest
from pathlib import Path
from crontab_lint import bookmark as bm_mod
from crontab_lint.cli_bookmarks import run_bookmarks


@pytest.fixture
def tmp_store(tmp_path):
    return tmp_path / "bookmarks.json"


def test_add_and_find(tmp_store):
    store = bm_mod.BookmarkStore()
    store.add("0 * * * *", "hourly")
    bm_mod.save(store, tmp_store)
    loaded = bm_mod.load(tmp_store)
    result = loaded.find("hourly")
    assert result is not None
    assert result.expression == "0 * * * *"


def test_find_missing_returns_none():
    store = bm_mod.BookmarkStore()
    assert store.find("nope") is None


def test_remove_existing():
    store = bm_mod.BookmarkStore()
    store.add("* * * * *", "every-min")
    removed = store.remove("every-min")
    assert removed is True
    assert store.find("every-min") is None


def test_remove_missing():
    store = bm_mod.BookmarkStore()
    assert store.remove("ghost") is False


def test_roundtrip_with_notes(tmp_store):
    store = bm_mod.BookmarkStore()
    store.add("0 0 * * *", "daily", notes="runs at midnight")
    bm_mod.save(store, tmp_store)
    loaded = bm_mod.load(tmp_store)
    b = loaded.find("daily")
    assert b.notes == "runs at midnight"


def test_load_missing_file(tmp_path):
    store = bm_mod.load(tmp_path / "nonexistent.json")
    assert store.all() == []


def test_cli_add(tmp_store):
    rc = run_bookmarks(["add", "0 * * * *", "hourly"], store_path=tmp_store)
    assert rc == 0
    store = bm_mod.load(tmp_store)
    assert store.find("hourly") is not None


def test_cli_find_existing(tmp_store, capsys):
    run_bookmarks(["add", "0 0 * * *", "daily"], store_path=tmp_store)
    rc = run_bookmarks(["find", "daily"], store_path=tmp_store)
    assert rc == 0
    out = capsys.readouterr().out
    assert "daily" in out


def test_cli_find_missing(tmp_store):
    rc = run_bookmarks(["find", "ghost"], store_path=tmp_store)
    assert rc == 1


def test_cli_remove(tmp_store):
    run_bookmarks(["add", "* * * * *", "every"], store_path=tmp_store)
    rc = run_bookmarks(["remove", "every"], store_path=tmp_store)
    assert rc == 0
    assert bm_mod.load(tmp_store).find("every") is None


def test_cli_list_empty(tmp_store, capsys):
    rc = run_bookmarks(["list"], store_path=tmp_store)
    assert rc == 0
    assert "No bookmarks" in capsys.readouterr().out


def test_cli_no_command_returns_zero(tmp_store):
    rc = run_bookmarks([], store_path=tmp_store)
    assert rc == 0
