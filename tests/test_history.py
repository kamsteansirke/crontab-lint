"""Tests for crontab_lint.history."""
import json
import os
import pytest

from crontab_lint.history import (
    History, HistoryEntry, load, save, record
)


@pytest.fixture
def tmp_file(tmp_path):
    return str(tmp_path / "history.json")


def test_history_add_and_recent():
    h = History()
    e = HistoryEntry(expression="* * * * *", valid=True, explanation="Every minute")
    h.add(e)
    assert len(h.recent(10)) == 1


def test_history_recent_limits():
    h = History()
    for i in range(15):
        h.add(HistoryEntry(expression=f"{i} * * * *", valid=True, explanation=None))
    assert len(h.recent(5)) == 5
    assert h.recent(5)[-1].expression == "14 * * * *"


def test_history_clear():
    h = History()
    h.add(HistoryEntry(expression="* * * * *", valid=True, explanation=None))
    h.clear()
    assert h.recent() == []


def test_save_and_load_roundtrip(tmp_file):
    h = History()
    h.add(HistoryEntry(expression="0 9 * * 1", valid=True, explanation="Monday 9am"))
    save(h, tmp_file)
    loaded = load(tmp_file)
    assert len(loaded.entries) == 1
    assert loaded.entries[0].expression == "0 9 * * 1"
    assert loaded.entries[0].explanation == "Monday 9am"


def test_load_missing_file(tmp_file):
    h = load(tmp_file)
    assert h.entries == []


def test_record_creates_file(tmp_file):
    entry = record("*/5 * * * *", valid=True, explanation="Every 5 min", path=tmp_file)
    assert os.path.exists(tmp_file)
    assert entry.expression == "*/5 * * * *"
    loaded = load(tmp_file)
    assert len(loaded.entries) == 1


def test_record_appends(tmp_file):
    record("* * * * *", valid=True, path=tmp_file)
    record("0 0 * * *", valid=True, path=tmp_file)
    h = load(tmp_file)
    assert len(h.entries) == 2
