"""Tests for expression_popularity and expression_popularity_formatter."""
import json
import pytest
from pathlib import Path

from crontab_lint.expression_popularity import (
    PopularityEntry,
    PopularityReport,
    PopularityStore,
)
from crontab_lint.expression_popularity_formatter import (
    format_entry,
    format_report,
    format_summary,
)


@pytest.fixture
def tmp_store(tmp_path: Path) -> PopularityStore:
    return PopularityStore(tmp_path / "popularity.json")


# --- PopularityEntry ---

def test_entry_to_dict_round_trip():
    e = PopularityEntry(expression="0 * * * *", count=3, last_seen="2024-01-01")
    assert PopularityEntry.from_dict(e.to_dict()) == e


def test_entry_from_dict_defaults():
    e = PopularityEntry.from_dict({"expression": "* * * * *"})
    assert e.count == 0
    assert e.last_seen is None


# --- PopularityStore ---

def test_record_increments_count(tmp_store: PopularityStore):
    tmp_store.record("* * * * *")
    tmp_store.record("* * * * *")
    entry = tmp_store.get("* * * * *")
    assert entry is not None
    assert entry.count == 2


def test_record_new_expression_starts_at_one(tmp_store: PopularityStore):
    entry = tmp_store.record("0 9 * * 1")
    assert entry.count == 1


def test_record_stores_timestamp(tmp_store: PopularityStore):
    tmp_store.record("0 0 * * *", timestamp="2024-06-01T00:00:00")
    entry = tmp_store.get("0 0 * * *")
    assert entry is not None
    assert entry.last_seen == "2024-06-01T00:00:00"


def test_get_missing_returns_none(tmp_store: PopularityStore):
    assert tmp_store.get("1 2 3 4 5") is None


def test_reset_removes_entry(tmp_store: PopularityStore):
    tmp_store.record("* * * * *")
    result = tmp_store.reset("* * * * *")
    assert result is True
    assert tmp_store.get("* * * * *") is None


def test_reset_missing_returns_false(tmp_store: PopularityStore):
    assert tmp_store.reset("not-there") is False


def test_persistence_across_instances(tmp_path: Path):
    p = tmp_path / "pop.json"
    s1 = PopularityStore(p)
    s1.record("0 * * * *")
    s2 = PopularityStore(p)
    assert s2.get("0 * * * *") is not None
    assert s2.get("0 * * * *").count == 1  # type: ignore[union-attr]


# --- PopularityReport ---

def test_top_n_returns_sorted(tmp_store: PopularityStore):
    for _ in range(3):
        tmp_store.record("* * * * *")
    tmp_store.record("0 9 * * 1")
    report = tmp_store.report()
    top = report.top_n(2)
    assert top[0].expression == "* * * * *"
    assert top[0].count == 3


def test_total_tracked(tmp_store: PopularityStore):
    tmp_store.record("* * * * *")
    tmp_store.record("0 0 * * *")
    assert tmp_store.report().total_tracked() == 2


# --- Formatter ---

def test_format_entry_contains_expression():
    e = PopularityEntry(expression="0 * * * *", count=5)
    assert "0 * * * *" in format_entry(e)


def test_format_entry_contains_count():
    e = PopularityEntry(expression="0 * * * *", count=5)
    assert "5" in format_entry(e)


def test_format_entry_with_index():
    e = PopularityEntry(expression="* * * * *", count=1)
    assert format_entry(e, index=1).startswith("1.")


def test_format_report_contains_expression(tmp_store: PopularityStore):
    tmp_store.record("0 12 * * *")
    report = tmp_store.report()
    assert "0 12 * * *" in format_report(report)


def test_format_report_empty_shows_no_data():
    report = PopularityReport()
    assert "No data" in format_report(report)


def test_format_summary_shows_tracked_count(tmp_store: PopularityStore):
    tmp_store.record("* * * * *")
    tmp_store.record("0 0 * * *")
    summary = format_summary(tmp_store.report())
    assert "2" in summary
