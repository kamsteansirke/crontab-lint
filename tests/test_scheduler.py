"""Tests for crontab_lint.scheduler."""

from datetime import datetime
import pytest
from crontab_lint.scheduler import next_run, next_n_runs, ScheduleError


BASE = datetime(2024, 1, 15, 10, 30)  # Monday


def test_next_run_every_minute():
    result = next_run("* * * * *", after=BASE)
    assert result == datetime(2024, 1, 15, 10, 31)


def test_next_run_specific_time():
    result = next_run("0 12 * * *", after=BASE)
    assert result == datetime(2024, 1, 15, 12, 0)


def test_next_run_specific_time_past_today():
    result = next_run("0 9 * * *", after=BASE)
    assert result == datetime(2024, 1, 16, 9, 0)


def test_next_run_day_of_week():
    # Next Friday from Monday 2024-01-15
    result = next_run("0 9 * * 5", after=BASE)
    assert result.weekday() == 4  # Friday
    assert result.hour == 9
    assert result.minute == 0


def test_next_run_step():
    result = next_run("*/15 * * * *", after=BASE)
    assert result == datetime(2024, 1, 15, 10, 45)


def test_next_run_range():
    result = next_run("0 9-11 * * *", after=BASE)
    assert result == datetime(2024, 1, 15, 11, 0)


def test_next_n_runs_returns_correct_count():
    results = next_n_runs("0 * * * *", n=3, after=BASE)
    assert len(results) == 3


def test_next_n_runs_are_ordered():
    results = next_n_runs("0 * * * *", n=5, after=BASE)
    for i in range(1, len(results)):
        assert results[i] > results[i - 1]


def test_next_n_runs_hourly():
    results = next_n_runs("0 * * * *", n=3, after=BASE)
    assert results[0] == datetime(2024, 1, 15, 11, 0)
    assert results[1] == datetime(2024, 1, 15, 12, 0)
    assert results[2] == datetime(2024, 1, 15, 13, 0)


def test_schedule_error_on_invalid_expression():
    with pytest.raises(ScheduleError):
        next_run("invalid", after=BASE)
