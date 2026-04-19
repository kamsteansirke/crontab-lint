"""Tests for crontab_lint.schedule_formatter."""

from datetime import datetime
from crontab_lint.schedule_formatter import (
    format_next_runs,
    format_schedule_error,
    format_schedule_block,
)

RUNS = [
    datetime(2024, 1, 15, 11, 0),
    datetime(2024, 1, 15, 12, 0),
    datetime(2024, 1, 15, 13, 0),
]


def test_format_next_runs_contains_expression():
    result = format_next_runs("0 * * * *", RUNS)
    assert "0 * * * *" in result


def test_format_next_runs_contains_all_times():
    result = format_next_runs("0 * * * *", RUNS)
    assert "2024-01-15 11:00" in result
    assert "2024-01-15 12:00" in result
    assert "2024-01-15 13:00" in result


def test_format_next_runs_numbered():
    result = format_next_runs("0 * * * *", RUNS)
    assert "1." in result
    assert "2." in result
    assert "3." in result


def test_format_schedule_error_contains_expression():
    result = format_schedule_error("bad expr", "parse failed")
    assert "bad expr" in result


def test_format_schedule_error_contains_message():
    result = format_schedule_error("bad expr", "parse failed")
    assert "parse failed" in result


def test_format_schedule_block_no_error_shows_runs():
    result = format_schedule_block("0 * * * *", RUNS)
    assert "2024-01-15 11:00" in result


def test_format_schedule_block_with_error_shows_error():
    result = format_schedule_block("bad", [], error="something went wrong")
    assert "something went wrong" in result
    assert "2024" not in result
