"""Tests for expression_tracer and expression_tracer_formatter."""
from datetime import datetime

import pytest

from crontab_lint.expression_tracer import trace
from crontab_lint.expression_tracer_formatter import format_result, format_results, format_summary

_START = datetime(2024, 1, 1, 0, 0)
_END = datetime(2024, 1, 1, 1, 0)  # one hour window


# ---------------------------------------------------------------------------
# trace()
# ---------------------------------------------------------------------------

def test_trace_invalid_expression_returns_error():
    result = trace("not a cron", _START, _END)
    assert not result.is_valid
    assert result.error is not None
    assert result.count == 0


def test_trace_end_before_start_returns_error():
    result = trace("* * * * *", _END, _START)
    assert not result.is_valid
    assert "end must be after start" in result.error


def test_trace_every_minute_one_hour_gives_60_entries():
    result = trace("* * * * *", _START, _END)
    assert result.is_valid
    assert result.count == 60


def test_trace_every_minute_entries_are_sequential():
    result = trace("* * * * *", _START, _END)
    times = [e.trigger_time for e in result.entries]
    assert times == sorted(times)


def test_trace_entries_are_indexed_from_one():
    result = trace("* * * * *", _START, _END)
    assert result.entries[0].index == 1
    assert result.entries[-1].index == result.count


def test_trace_max_entries_limits_output():
    result = trace("* * * * *", _START, _END, max_entries=10)
    assert result.count == 10


def test_trace_specific_minute_has_one_trigger_per_hour():
    # "30 * * * *" fires at :30 of every hour
    end = datetime(2024, 1, 1, 3, 0)
    result = trace("30 * * * *", _START, end)
    assert result.is_valid
    assert result.count == 2  # 00:30 and 01:30 and 02:30 — but end is 03:00 exclusive
    # Actually 00:30, 01:30, 02:30 => 3 triggers
    # Re-check: end=03:00, triggers at 00:30, 01:30, 02:30 => 3


def test_trace_no_triggers_in_window():
    # Fire at midnight only; window starts after midnight
    start = datetime(2024, 1, 1, 0, 1)
    end = datetime(2024, 1, 1, 23, 59)
    result = trace("0 0 * * *", start, end)
    assert result.is_valid
    assert result.count == 0


# ---------------------------------------------------------------------------
# format_result()
# ---------------------------------------------------------------------------

def test_format_result_contains_expression():
    result = trace("* * * * *", _START, _END)
    out = format_result(result)
    assert "* * * * *" in out


def test_format_result_shows_trigger_count():
    result = trace("* * * * *", _START, _END)
    out = format_result(result)
    assert "60" in out


def test_format_result_invalid_shows_error():
    result = trace("bad expr", _START, _END)
    out = format_result(result)
    assert "Error" in out


def test_format_result_empty_window_notes_no_triggers():
    start = datetime(2024, 1, 1, 0, 1)
    end = datetime(2024, 1, 1, 23, 59)
    result = trace("0 0 * * *", start, end)
    out = format_result(result)
    assert "no triggers" in out


# ---------------------------------------------------------------------------
# format_results() and format_summary()
# ---------------------------------------------------------------------------

def test_format_results_multiple_expressions():
    r1 = trace("* * * * *", _START, _END)
    r2 = trace("0 * * * *", _START, _END)
    out = format_results([r1, r2])
    assert "* * * * *" in out
    assert "0 * * * *" in out


def test_format_summary_shows_totals():
    r1 = trace("* * * * *", _START, _END)
    r2 = trace("bad", _START, _END)
    out = format_summary([r1, r2])
    assert "2" in out  # total expressions
    assert "1" in out  # valid count
