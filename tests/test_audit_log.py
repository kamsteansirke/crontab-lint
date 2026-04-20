"""Tests for audit_log and audit_log_formatter."""

import json
import os
import pytest

from crontab_lint.audit_log import AuditEntry, AuditLog
from crontab_lint.audit_log_formatter import (
    format_entry,
    format_audit_log,
    format_summary,
)


@pytest.fixture
def tmp_log(tmp_path):
    return AuditLog(str(tmp_path / "audit.json"))


def _make(action="lint", expression="* * * * *", actor=None, detail=None):
    return AuditEntry.create(action, expression, actor, detail)


# --- AuditLog ---

def test_record_and_recent(tmp_log):
    tmp_log.record(_make())
    tmp_log.record(_make(action="add"))
    assert len(tmp_log.recent()) == 2


def test_recent_limits(tmp_log):
    for _ in range(10):
        tmp_log.record(_make())
    assert len(tmp_log.recent(3)) == 3


def test_filter_by_action(tmp_log):
    tmp_log.record(_make(action="lint"))
    tmp_log.record(_make(action="add"))
    tmp_log.record(_make(action="lint"))
    assert len(tmp_log.filter_by_action("lint")) == 2


def test_filter_by_actor(tmp_log):
    tmp_log.record(_make(actor="alice"))
    tmp_log.record(_make(actor="bob"))
    assert len(tmp_log.filter_by_actor("alice")) == 1


def test_clear(tmp_log):
    tmp_log.record(_make())
    tmp_log.clear()
    assert len(tmp_log) == 0


def test_persistence(tmp_path):
    path = str(tmp_path / "audit.json")
    log1 = AuditLog(path)
    log1.record(_make(action="edit", detail="changed schedule"))
    log2 = AuditLog(path)
    assert len(log2) == 1
    assert log2.recent()[0].action == "edit"
    assert log2.recent()[0].detail == "changed schedule"


# --- Formatter ---

def test_format_entry_contains_action():
    e = _make(action="add", expression="0 9 * * 1")
    result = format_entry(e)
    assert "ADD" in result
    assert "0 9 * * 1" in result


def test_format_entry_with_index():
    e = _make()
    result = format_entry(e, index=3)
    assert result.startswith("3.")


def test_format_entry_with_actor_and_detail():
    e = _make(actor="alice", detail="routine check")
    result = format_entry(e)
    assert "alice" in result
    assert "routine check" in result


def test_format_audit_log_empty():
    assert "No audit" in format_audit_log([])


def test_format_audit_log_multiple():
    entries = [_make(), _make(action="remove")]
    result = format_audit_log(entries)
    assert "1." in result
    assert "2." in result


def test_format_summary_counts():
    entries = [_make(), _make(), _make(action="add")]
    result = format_summary(entries)
    assert "lint: 2" in result
    assert "add: 1" in result


def test_format_summary_empty():
    assert "empty" in format_summary([]).lower()
