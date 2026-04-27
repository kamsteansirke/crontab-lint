"""Tests for expression_inspector."""
import pytest
from crontab_lint.expression_inspector import inspect, InspectionResult


def test_inspect_returns_inspection_result():
    result = inspect("0 9 * * 1")
    assert isinstance(result, InspectionResult)


def test_inspect_valid_expression_is_valid():
    result = inspect("0 9 * * 1")
    assert result.is_valid is True


def test_inspect_valid_expression_has_no_error():
    result = inspect("0 9 * * 1")
    assert result.error is None


def test_inspect_invalid_expression_is_not_valid():
    result = inspect("not a cron")
    assert result.is_valid is False


def test_inspect_invalid_expression_has_error():
    result = inspect("not a cron")
    assert result.error is not None
    assert len(result.error) > 0


def test_inspect_invalid_expression_other_fields_are_none():
    result = inspect("not a cron")
    assert result.explanation is None
    assert result.frequency_category is None
    assert result.score_total is None
    assert result.complexity_label is None
    assert result.cost_level is None


def test_inspect_valid_has_explanation():
    result = inspect("0 0 * * *")
    assert result.explanation is not None
    assert len(result.explanation) > 0


def test_inspect_valid_has_tags():
    result = inspect("* * * * *")
    assert isinstance(result.tags, list)
    assert len(result.tags) > 0


def test_inspect_every_minute_frequency_category():
    result = inspect("* * * * *")
    assert result.frequency_category is not None


def test_inspect_every_minute_runs_per_day():
    result = inspect("* * * * *")
    assert result.runs_per_day is not None
    assert result.runs_per_day == pytest.approx(1440, rel=0.01)


def test_inspect_valid_has_score():
    result = inspect("0 6 * * *")
    assert result.score_total is not None
    assert isinstance(result.score_total, int)


def test_inspect_valid_has_grade():
    result = inspect("0 6 * * *")
    assert result.score_grade is not None
    assert result.score_grade in ("A", "B", "C", "D", "F")


def test_inspect_valid_has_complexity_label():
    result = inspect("0 6 * * *")
    assert result.complexity_label is not None


def test_inspect_valid_has_cost_level():
    result = inspect("0 6 * * *")
    assert result.cost_level is not None


def test_inspect_strips_whitespace():
    result = inspect("  0 6 * * *  ")
    assert result.is_valid is True


def test_inspect_special_string_daily():
    result = inspect("@daily")
    assert result.is_valid is True
    assert result.explanation is not None
