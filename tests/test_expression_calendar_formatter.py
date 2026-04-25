"""Tests for expression_calendar_formatter module."""

from datetime import datetime

import pytest

from crontab_lint.expression_calendar import build_calendar
from crontab_lint.expression_calendar_formatter import (
    format_calendar,
    format_day,
    format_summary,
)

_START = datetime(2024, 3, 1, 0, 0)


def _view(expr: str, days: int = 7):
    return build_calendar(expr, start=_START, days=days)


def test_format_calendar_contains_expression():
    view = _view("0 9 * * *")
    output = format_calendar(view)
    assert "0 9 * * *" in output


def test_format_calendar_shows_range():
    view = _view("0 9 * * *", days=5)
    output = format_calendar(view)
    assert "2024-03-01" in output
    assert "5 days" in output


def test_format_calendar_shows_total_runs():
    view = _view("0 9 * * *", days=7)
    output = format_calendar(view)
    assert "Total runs" in output
    assert "7" in output


def test_format_calendar_invalid_shows_error():
    view = _view("not valid")
    output = format_calendar(view)
    assert "ERROR" in output


def test_format_day_contains_date():
    view = _view("0 9 * * *")
    day = view.calendar[0]
    line = format_day(day, max_count=1)
    assert "2024-03-01" in line


def test_format_day_contains_count():
    view = _view("0 9 * * *")
    day = view.calendar[0]
    line = format_day(day, max_count=5)
    assert "1" in line


def test_format_day_with_index():
    view = _view("0 9 * * *")
    day = view.calendar[0]
    line = format_day(day, max_count=1, index=3)
    assert "3." in line


def test_format_summary_contains_all_expressions():
    views = [_view("0 9 * * *"), _view("*/15 * * * *")]
    output = format_summary(views)
    assert "0 9 * * *" in output
    assert "*/15 * * * *" in output


def test_format_summary_shows_run_count():
    views = [_view("0 9 * * *", days=7)]
    output = format_summary(views)
    assert "runs" in output


def test_format_summary_invalid_shows_error():
    views = [_view("bad expr")]
    output = format_summary(views)
    assert "ERROR" in output
