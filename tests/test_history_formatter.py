"""Tests for crontab_lint.history_formatter."""
from crontab_lint.history import HistoryEntry
from crontab_lint.history_formatter import format_entry, format_history, format_summary


def _entry(expr="* * * * *", valid=True, explanation=None):
    return HistoryEntry(expression=expr, valid=valid, explanation=explanation,
                        timestamp="2024-01-01T00:00:00")


def test_format_entry_valid():
    result = format_entry(_entry(), index=1)
    assert "VALID" in result
    assert "* * * * *" in result
    assert "1." in result


def test_format_entry_invalid():
    result = format_entry(_entry(valid=False), index=2)
    assert "INVALID" in result


def test_format_entry_with_explanation():
    result = format_entry(_entry(explanation="Every minute"))
    assert "Every minute" in result


def test_format_entry_no_index():
    result = format_entry(_entry())
    assert result.startswith(" ")


def test_format_history_empty():
    result = format_history([])
    assert "No history" in result


def test_format_history_multiple():
    entries = [_entry("* * * * *"), _entry("0 9 * * 1", valid=False)]
    result = format_history(entries)
    assert "* * * * *" in result
    assert "0 9 * * 1" in result


def test_format_summary_counts():
    entries = [_entry(valid=True), _entry(valid=True), _entry(valid=False)]
    result = format_summary(entries)
    assert "3 total" in result
    assert "2 valid" in result
    assert "1 invalid" in result


def test_format_summary_empty():
    result = format_summary([])
    assert "0 total" in result
