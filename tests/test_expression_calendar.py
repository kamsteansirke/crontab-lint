"""Tests for expression_calendar module."""

from datetime import datetime

import pytest

from crontab_lint.expression_calendar import build_calendar, CalendarView, CalendarDay

_START = datetime(2024, 1, 15, 0, 0)


def test_invalid_expression_returns_error():
    view = build_calendar("not a cron", start=_START, days=3)
    assert not view.is_valid
    assert view.error
    assert view.total_runs == 0


def test_valid_expression_returns_calendar():
    view = build_calendar("0 9 * * *", start=_START, days=5)
    assert view.is_valid
    assert len(view.calendar) == 5


def test_calendar_days_match_requested_count():
    for n in (1, 3, 7, 14):
        view = build_calendar("0 12 * * *", start=_START, days=n)
        assert len(view.calendar) == n


def test_every_minute_has_runs_every_day():
    view = build_calendar("* * * * *", start=_START, days=3)
    assert view.is_valid
    for day in view.calendar:
        assert day.count > 0


def test_once_daily_has_one_run_per_day():
    view = build_calendar("0 8 * * *", start=_START, days=5)
    assert view.is_valid
    # Each day should have exactly one run (08:00)
    for day in view.calendar:
        assert day.count == 1


def test_total_runs_sums_all_days():
    view = build_calendar("0 8 * * *", start=_START, days=7)
    assert view.total_runs == sum(d.count for d in view.calendar)


def test_calendar_day_dates_are_sequential():
    view = build_calendar("0 6 * * *", start=_START, days=4)
    dates = [d.date for d in view.calendar]
    for i in range(1, len(dates)):
        delta = dates[i] - dates[i - 1]
        assert delta.days == 1


def test_run_times_within_day_bounds():
    view = build_calendar("*/30 * * * *", start=_START, days=2)
    for day in view.calendar:
        for run in day.run_times:
            assert run.date() == day.date.date()


def test_default_start_is_used_when_none():
    view = build_calendar("0 0 * * *", days=3)
    assert view.is_valid
    assert len(view.calendar) == 3


def test_expression_stored_on_view():
    expr = "5 4 * * 0"
    view = build_calendar(expr, start=_START, days=7)
    assert view.expression == expr
