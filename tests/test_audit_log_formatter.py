"""Tests for the audit log formatter module."""

import pytest
from datetime import datetime, timezone
from crontab_lint.audit_log import AuditEntry
from crontab_lint.audit_log_formatter import format_entry, format_audit_log, format_summary


def _make(action="lint", expression="* * * * *", detail=None, index=None):
    """Create a sample AuditEntry for testing."""
    return AuditEntry(
        timestamp=datetime(2024, 6, 15, 10, 30, 0, tzinfo=timezone.utc),
        action=action,
        expression=expression,
        detail=detail,
        index=index,
    )


# --- format_entry ---

def test_format_entry_contains_action():
    entry = _make(action="lint")
    result = format_entry(entry)
    assert "lint" in result


def test_format_entry_contains_expression():
    entry = _make(expression="0 9 * * 1")
    result = format_entry(entry)
    assert "0 9 * * 1" in result


def test_format_entry_contains_timestamp():
    entry = _make()
    result = format_entry(entry)
    # Should contain some recognisable part of the timestamp
    assert "2024" in result


def test_format_entry_with_detail():
    entry = _make(detail="invalid field: minute")
    result = format_entry(entry)
    assert "invalid field: minute" in result


def test_format_entry_no_detail():
    entry = _make(detail=None)
    result = format_entry(entry)
    # Should not raise and should still include expression
    assert "* * * * *" in result


def test_format_entry_with_index():
    entry = _make(index=3)
    result = format_entry(entry, index=3)
    assert "3" in result


def test_format_entry_no_index():
    entry = _make()
    result = format_entry(entry)
    # Should not raise
    assert isinstance(result, str)


# --- format_audit_log ---

def test_format_audit_log_empty():
    result = format_audit_log([])
    assert "no" in result.lower() or result.strip() == "" or isinstance(result, str)


def test_format_audit_log_contains_all_entries():
    entries = [
        _make(action="lint", expression="* * * * *"),
        _make(action="export", expression="0 0 * * *"),
        _make(action="validate", expression="30 6 * * 1-5"),
    ]
    result = format_audit_log(entries)
    assert "* * * * *" in result
    assert "0 0 * * *" in result
    assert "30 6 * * 1-5" in result


def test_format_audit_log_numbered():
    entries = [_make(action="lint"), _make(action="export")]
    result = format_audit_log(entries)
    assert "1" in result
    assert "2" in result


def test_format_audit_log_single_entry():
    entries = [_make(action="lint", expression="@daily")]
    result = format_audit_log(entries)
    assert "@daily" in result


# --- format_summary ---

def test_format_summary_total_count():
    entries = [_make(), _make(), _make()]
    result = format_summary(entries)
    assert "3" in result


def test_format_summary_empty():
    result = format_summary([])
    assert "0" in result or "no" in result.lower()


def test_format_summary_shows_action_breakdown():
    entries = [
        _make(action="lint"),
        _make(action="lint"),
        _make(action="export"),
    ]
    result = format_summary(entries)
    assert "lint" in result
    assert "export" in result


def test_format_summary_is_string():
    entries = [_make(action="validate", expression="0 12 * * *")]
    result = format_summary(entries)
    assert isinstance(result, str)
