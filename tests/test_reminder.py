"""Tests for reminder.py and reminder_formatter.py."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from crontab_lint.reminder import Reminder, ReminderStore
from crontab_lint.reminder_formatter import (
    format_reminder,
    format_reminders,
    format_summary,
)


@pytest.fixture
def tmp_store(tmp_path: Path) -> ReminderStore:
    return ReminderStore(tmp_path / "reminders.json")


def _make(note: str = "check logs", due: str | None = None) -> Reminder:
    return Reminder(expression="0 * * * *", note=note, due=due)


# ---------------------------------------------------------------------------
# Reminder model
# ---------------------------------------------------------------------------

def test_is_overdue_no_due():
    assert _make().is_overdue() is False


def test_is_overdue_future():
    r = _make(due="2099-01-01")
    assert r.is_overdue() is False


def test_is_overdue_past():
    r = _make(due="2000-01-01")
    assert r.is_overdue() is True


def test_is_overdue_invalid_date():
    r = _make(due="not-a-date")
    assert r.is_overdue() is False


# ---------------------------------------------------------------------------
# ReminderStore
# ---------------------------------------------------------------------------

def test_add_and_all(tmp_store: ReminderStore):
    tmp_store.add(_make("note-a"))
    tmp_store.add(_make("note-b"))
    assert len(tmp_store.all()) == 2


def test_remove_existing(tmp_store: ReminderStore):
    tmp_store.add(_make("to-remove"))
    assert tmp_store.remove("to-remove") is True
    assert tmp_store.all() == []


def test_remove_missing(tmp_store: ReminderStore):
    assert tmp_store.remove("ghost") is False


def test_find_by_expression(tmp_store: ReminderStore):
    tmp_store.add(Reminder(expression="*/5 * * * *", note="five-min"))
    tmp_store.add(_make("other"))
    results = tmp_store.find_by_expression("*/5 * * * *")
    assert len(results) == 1
    assert results[0].note == "five-min"


def test_overdue_filter(tmp_store: ReminderStore):
    tmp_store.add(_make("past", due="2000-06-01"))
    tmp_store.add(_make("future", due="2099-06-01"))
    assert len(tmp_store.overdue()) == 1


def test_persistence_roundtrip(tmp_path: Path):
    p = tmp_path / "rem.json"
    s1 = ReminderStore(p)
    s1.add(Reminder(expression="@daily", note="daily job", tags=["prod"]))
    s2 = ReminderStore(p)
    assert len(s2.all()) == 1
    assert s2.all()[0].tags == ["prod"]


# ---------------------------------------------------------------------------
# Formatter
# ---------------------------------------------------------------------------

def test_format_reminder_contains_note():
    r = _make("my note")
    assert "my note" in format_reminder(r)


def test_format_reminder_shows_due():
    r = _make(due="2099-03-15")
    assert "2099-03-15" in format_reminder(r)


def test_format_reminder_overdue_flag():
    r = _make(due="2000-01-01")
    assert "OVERDUE" in format_reminder(r)


def test_format_reminders_empty():
    assert "No reminders" in format_reminders([])


def test_format_reminders_numbered():
    reminders = [_make(f"note-{i}") for i in range(3)]
    out = format_reminders(reminders)
    assert "1." in out and "3." in out


def test_format_summary_counts():
    reminders = [_make("a", due="2000-01-01"), _make("b")]
    out = format_summary(reminders)
    assert "Total reminders: 2" in out
    assert "Overdue: 1" in out
