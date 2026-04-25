"""Tests for expression_cost_estimator and its formatter."""
import pytest

from crontab_lint.expression_cost_estimator import estimate, CostEstimate
from crontab_lint.expression_cost_estimator_formatter import (
    format_estimate,
    format_estimates,
    format_summary,
)


# --- estimate() ---

def test_invalid_expression_returns_invalid():
    result = estimate("not a cron")
    assert result.is_valid is False
    assert result.error is not None


def test_every_minute_is_valid():
    result = estimate("* * * * *")
    assert result.is_valid is True


def test_every_minute_cost_level_very_high():
    result = estimate("* * * * *")
    assert result.cost_level == "very_high"


def test_every_minute_runs_per_day():
    result = estimate("* * * * *")
    assert result.runs_per_day == pytest.approx(1440, rel=0.05)


def test_once_daily_cost_level_low():
    result = estimate("0 3 * * *")
    assert result.cost_level == "low"


def test_once_daily_runs_per_day():
    result = estimate("0 3 * * *")
    assert result.runs_per_day == pytest.approx(1, rel=0.1)


def test_runs_per_week_is_seven_times_per_day():
    result = estimate("0 3 * * *")
    assert result.runs_per_week == pytest.approx(result.runs_per_day * 7, rel=0.01)


def test_runs_per_month_is_thirty_times_per_day():
    result = estimate("0 3 * * *")
    assert result.runs_per_month == pytest.approx(result.runs_per_day * 30, rel=0.01)


def test_every_minute_has_notes():
    result = estimate("* * * * *")
    assert len(result.notes) > 0


def test_once_daily_notes_mention_low_impact():
    result = estimate("0 3 * * *")
    assert any("low" in n.lower() for n in result.notes)


# --- format_estimate() ---

def test_format_estimate_contains_expression():
    result = estimate("0 3 * * *")
    text = format_estimate(result)
    assert "0 3 * * *" in text


def test_format_estimate_shows_cost_level():
    result = estimate("* * * * *")
    text = format_estimate(result)
    assert "VERY HIGH" in text or "very_high" in text.lower()


def test_format_estimate_invalid_shows_invalid():
    result = estimate("bad expr")
    text = format_estimate(result)
    assert "INVALID" in text


def test_format_estimate_with_index():
    result = estimate("0 3 * * *")
    text = format_estimate(result, index=3)
    assert text.startswith("3.")


# --- format_estimates() ---

def test_format_estimates_empty_returns_message():
    text = format_estimates([])
    assert "No estimates" in text


def test_format_estimates_numbers_entries():
    results = [estimate("* * * * *"), estimate("0 3 * * *")]
    text = format_estimates(results)
    assert "1." in text
    assert "2." in text


# --- format_summary() ---

def test_format_summary_shows_totals():
    results = [estimate("* * * * *"), estimate("0 3 * * *"), estimate("bad")]
    text = format_summary(results)
    assert "3" in text
    assert "Invalid" in text


def test_format_summary_empty():
    text = format_summary([])
    assert "No expressions" in text
