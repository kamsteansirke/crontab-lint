"""Tests for crontab_lint.frequency_analyzer."""

import pytest
from crontab_lint.frequency_analyzer import analyze, FrequencyAnalysis


def test_every_minute_is_valid():
    result = analyze("* * * * *")
    assert result.is_valid is True
    assert result.error is None


def test_every_minute_is_high_frequency():
    result = analyze("* * * * *")
    assert result.category == "high"
    assert result.estimated_runs_per_day is not None
    assert result.estimated_runs_per_day >= 1440


def test_once_daily_category():
    result = analyze("0 6 * * *")
    assert result.is_valid is True
    assert result.category in ("low", "medium")
    assert result.estimated_runs_per_day is not None
    assert 0.9 <= result.estimated_runs_per_day <= 1.1


def test_once_weekly_is_rare():
    result = analyze("0 0 * * 0")
    assert result.is_valid is True
    assert result.category == "rare"


def test_hourly_special_string():
    result = analyze("@hourly")
    assert result.is_valid is True
    assert result.estimated_runs_per_day == pytest.approx(24.0)
    assert result.category in ("medium", "low")


def test_daily_special_string():
    result = analyze("@daily")
    assert result.is_valid is True
    assert result.estimated_runs_per_day == pytest.approx(1.0)


def test_weekly_special_string():
    result = analyze("@weekly")
    assert result.is_valid is True
    assert result.category == "rare"


def test_reboot_special_string():
    result = analyze("@reboot")
    assert result.is_valid is True
    assert result.estimated_runs_per_day is None
    assert result.category == "rare"
    assert "reboot" in result.description


def test_invalid_expression_returns_error():
    result = analyze("not a cron")
    assert result.is_valid is False
    assert result.error is not None
    assert result.category is None
    assert result.estimated_runs_per_day is None


def test_monthly_special_string():
    result = analyze("@monthly")
    assert result.is_valid is True
    assert result.category == "rare"


def test_multiple_times_per_hour():
    # Every 5 minutes
    result = analyze("*/5 * * * *")
    assert result.is_valid is True
    assert result.estimated_runs_per_day is not None
    assert result.estimated_runs_per_day > 24
    assert result.category == "high"


def test_description_is_string():
    result = analyze("0 9 * * 1-5")
    assert result.is_valid is True
    assert isinstance(result.description, str)
    assert len(result.description) > 0


def test_yearly_special_string():
    result = analyze("@yearly")
    assert result.is_valid is True
    assert result.category == "rare"
    assert result.estimated_runs_per_day == pytest.approx(1 / 365, rel=1e-3)
