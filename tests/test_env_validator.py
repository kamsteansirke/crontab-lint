"""Tests for crontab_lint.env_validator."""
import pytest
from crontab_lint.env_validator import (
    EnvConstraint,
    EnvViolation,
    EnvValidationResult,
    validate_against_env,
    _parse_field_ints,
)


# ---------------------------------------------------------------------------
# _parse_field_ints helpers
# ---------------------------------------------------------------------------

def test_parse_wildcard():
    assert _parse_field_ints("*", 0, 5) == [0, 1, 2, 3, 4, 5]


def test_parse_specific():
    assert _parse_field_ints("3", 0, 23) == [3]


def test_parse_range():
    assert _parse_field_ints("1-3", 0, 23) == [1, 2, 3]


def test_parse_step():
    assert _parse_field_ints("*/15", 0, 59) == [0, 15, 30, 45]


def test_parse_list():
    assert _parse_field_ints("1,3,5", 0, 6) == [1, 3, 5]


# ---------------------------------------------------------------------------
# validate_against_env – parse error
# ---------------------------------------------------------------------------

def test_invalid_expression_returns_violation():
    c = EnvConstraint(name="prod")
    result = validate_against_env("not a cron", c)
    assert not result.valid
    assert any("Parse error" in v.message for v in result.violations)


# ---------------------------------------------------------------------------
# allowed_hours
# ---------------------------------------------------------------------------

def test_allowed_hours_passes():
    c = EnvConstraint(name="prod", allowed_hours=list(range(8, 20)))
    result = validate_against_env("0 9 * * *", c)
    assert result.valid


def test_allowed_hours_violation():
    c = EnvConstraint(name="prod", allowed_hours=list(range(8, 20)))
    result = validate_against_env("0 3 * * *", c)
    assert not result.valid
    assert any("restricted hours" in v.message for v in result.violations)


def test_no_hour_constraint_passes_any_hour():
    c = EnvConstraint(name="dev")
    result = validate_against_env("0 3 * * *", c)
    assert result.valid


# ---------------------------------------------------------------------------
# allowed_weekdays
# ---------------------------------------------------------------------------

def test_allowed_weekdays_passes():
    # Mon-Fri = 1-5
    c = EnvConstraint(name="prod", allowed_weekdays=[1, 2, 3, 4, 5])
    result = validate_against_env("0 9 * * 1-5", c)
    assert result.valid


def test_allowed_weekdays_violation():
    c = EnvConstraint(name="prod", allowed_weekdays=[1, 2, 3, 4, 5])
    result = validate_against_env("0 9 * * 0", c)  # Sunday
    assert not result.valid
    assert any("restricted weekdays" in v.message for v in result.violations)


# ---------------------------------------------------------------------------
# max_frequency_minutes
# ---------------------------------------------------------------------------

def test_frequency_passes_when_gap_sufficient():
    c = EnvConstraint(name="prod", max_frequency_minutes=10)
    result = validate_against_env("0 * * * *", c)  # once per hour
    assert result.valid


def test_frequency_violation_every_minute():
    c = EnvConstraint(name="prod", max_frequency_minutes=10)
    result = validate_against_env("* * * * *", c)  # every minute
    assert not result.valid
    assert any("Frequency gap" in v.message for v in result.violations)


# ---------------------------------------------------------------------------
# multiple violations
# ---------------------------------------------------------------------------

def test_multiple_violations_collected():
    c = EnvConstraint(
        name="strict",
        allowed_hours=list(range(9, 17)),
        max_frequency_minutes=30,
    )
    # Runs at 2 AM every 5 minutes — two violations
    result = validate_against_env("*/5 2 * * *", c)
    assert not result.valid
    assert len(result.violations) >= 2
