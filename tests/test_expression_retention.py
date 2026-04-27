"""Tests for crontab_lint.expression_retention."""
import pytest

from crontab_lint.expression_retention import (
    RetentionResult,
    RetentionViolation,
    check,
    check_many,
)


# ---------------------------------------------------------------------------
# check() – basic validity
# ---------------------------------------------------------------------------

def test_check_returns_retention_result():
    result = check("* * * * *")
    assert isinstance(result, RetentionResult)


def test_check_invalid_expression_is_not_valid():
    result = check("not a cron")
    assert not result.is_valid


def test_check_invalid_expression_has_error():
    result = check("not a cron")
    assert result.error is not None
    assert len(result.error) > 0


def test_check_valid_expression_is_valid():
    result = check("* * * * *")
    assert result.is_valid


def test_check_no_bounds_passes():
    result = check("0 0 * * *")
    assert result.passed


def test_check_runs_per_day_is_set():
    result = check("* * * * *")
    assert result.runs_per_day is not None
    assert result.runs_per_day > 0


# ---------------------------------------------------------------------------
# min_runs_per_day
# ---------------------------------------------------------------------------

def test_min_runs_per_day_satisfied():
    # every minute => 1440 runs/day, min=1 should pass
    result = check("* * * * *", min_runs_per_day=1)
    assert result.passed


def test_min_runs_per_day_violated():
    # once daily => ~1 run/day, min=10 should fail
    result = check("0 0 * * *", min_runs_per_day=10)
    assert not result.passed
    assert any(v.rule == "min_runs_per_day" for v in result.violations)


def test_min_runs_per_day_violation_message():
    result = check("0 0 * * *", min_runs_per_day=10)
    violation = next(v for v in result.violations if v.rule == "min_runs_per_day")
    assert "minimum" in violation.message.lower()


# ---------------------------------------------------------------------------
# max_runs_per_day
# ---------------------------------------------------------------------------

def test_max_runs_per_day_satisfied():
    # once daily => 1 run/day, max=10 should pass
    result = check("0 0 * * *", max_runs_per_day=10)
    assert result.passed


def test_max_runs_per_day_violated():
    # every minute => 1440 runs/day, max=100 should fail
    result = check("* * * * *", max_runs_per_day=100)
    assert not result.passed
    assert any(v.rule == "max_runs_per_day" for v in result.violations)


def test_max_runs_per_day_violation_message():
    result = check("* * * * *", max_runs_per_day=100)
    violation = next(v for v in result.violations if v.rule == "max_runs_per_day")
    assert "maximum" in violation.message.lower()


# ---------------------------------------------------------------------------
# both bounds
# ---------------------------------------------------------------------------

def test_both_bounds_satisfied():
    # hourly => 24 runs/day; min=10, max=100 should pass
    result = check("0 * * * *", min_runs_per_day=10, max_runs_per_day=100)
    assert result.passed


def test_both_bounds_violated_too_low():
    result = check("0 0 * * *", min_runs_per_day=5, max_runs_per_day=100)
    assert not result.passed


# ---------------------------------------------------------------------------
# check_many()
# ---------------------------------------------------------------------------

def test_check_many_returns_list():
    results = check_many(["* * * * *", "0 0 * * *"])
    assert isinstance(results, list)
    assert len(results) == 2


def test_check_many_applies_bounds_to_all():
    results = check_many(["* * * * *", "0 0 * * *"], max_runs_per_day=100)
    # every-minute violates, once-daily passes
    assert not results[0].passed
    assert results[1].passed
