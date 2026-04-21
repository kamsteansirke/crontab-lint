"""Tests for crontab_lint.complexity_analyzer."""
import pytest
from crontab_lint.complexity_analyzer import analyze, ComplexityResult


def test_every_minute_is_simple():
    result = analyze("* * * * *")
    assert result.is_valid
    assert result.level == "simple"
    assert result.total == 0


def test_specific_time_is_simple():
    result = analyze("30 6 * * *")
    assert result.is_valid
    assert result.level == "simple"


def test_step_expression_adds_complexity():
    result = analyze("*/5 * * * *")
    assert result.is_valid
    assert result.total >= 1
    categories = [d.category for d in result.details]
    assert "minute" in categories


def test_range_expression_adds_complexity():
    result = analyze("0 9-17 * * *")
    assert result.is_valid
    assert result.total >= 1
    categories = [d.category for d in result.details]
    assert "hour" in categories


def test_list_expression_adds_complexity():
    result = analyze("0 6,12,18 * * *")
    assert result.is_valid
    # 3 tokens => 2 extra points
    assert result.total >= 2


def test_combined_complexity_is_moderate_or_higher():
    result = analyze("*/10 8-18 * * 1,2,3")
    assert result.is_valid
    assert result.level in ("moderate", "complex", "very_complex")


def test_invalid_expression_returns_invalid():
    result = analyze("not a cron")
    assert not result.is_valid
    assert result.error != ""
    assert result.total == 0


def test_special_string_daily():
    result = analyze("@daily")
    assert result.is_valid
    assert result.level == "simple"


def test_details_contain_reason():
    result = analyze("0 */2 * * *")
    assert result.is_valid
    assert any(d.reason for d in result.details)


def test_very_complex_expression():
    # Many list items across multiple fields
    result = analyze("1,2,3,4,5 1,2,3,4,5 * * 1,2,3")
    assert result.is_valid
    assert result.level in ("complex", "very_complex")


def test_level_thresholds():
    from crontab_lint.complexity_analyzer import _level
    assert _level(0) == "simple"
    assert _level(2) == "simple"
    assert _level(3) == "moderate"
    assert _level(5) == "moderate"
    assert _level(6) == "complex"
    assert _level(9) == "complex"
    assert _level(10) == "very_complex"
