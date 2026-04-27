"""Tests for expression_comparator module."""
import pytest
from crontab_lint.expression_comparator import compare, FieldDiff, FIELD_NAMES


def test_compare_identical_expressions_no_differences():
    result = compare("0 9 * * 1", "0 9 * * 1")
    assert result.valid
    assert not result.has_differences


def test_compare_identical_expressions_no_changed_fields():
    result = compare("0 9 * * 1", "0 9 * * 1")
    assert result.changed_fields == []


def test_compare_different_minute_field():
    result = compare("0 9 * * 1", "30 9 * * 1")
    assert result.valid
    assert result.has_differences
    changed = [d.name for d in result.changed_fields]
    assert "minute" in changed


def test_compare_different_hour_field():
    result = compare("0 9 * * *", "0 12 * * *")
    assert result.valid
    changed = [d.name for d in result.changed_fields]
    assert "hour" in changed


def test_compare_all_field_names_present():
    result = compare("* * * * *", "* * * * *")
    names = [d.name for d in result.field_diffs]
    assert names == FIELD_NAMES


def test_compare_invalid_left_expression():
    result = compare("invalid", "0 9 * * *")
    assert not result.valid
    assert result.error is not None


def test_compare_invalid_right_expression():
    result = compare("0 9 * * *", "bad expr")
    assert not result.valid
    assert result.error is not None


def test_compare_stores_left_and_right():
    result = compare("0 9 * * *", "0 10 * * *")
    assert result.left == "0 9 * * *"
    assert result.right == "0 10 * * *"


def test_compare_provides_explanations_when_valid():
    result = compare("0 9 * * *", "0 10 * * *")
    assert result.valid
    assert result.left_explanation is not None
    assert result.right_explanation is not None


def test_compare_no_explanations_when_invalid():
    result = compare("bad", "also bad")
    assert not result.valid
    assert result.left_explanation is None
    assert result.right_explanation is None


def test_compare_field_diff_changed_flag():
    result = compare("0 9 * * *", "0 9 * * 1")
    dow_diff = next(d for d in result.field_diffs if d.name == "day_of_week")
    assert dow_diff.changed
    minute_diff = next(d for d in result.field_diffs if d.name == "minute")
    assert not minute_diff.changed


def test_compare_special_string_daily():
    result = compare("@daily", "@daily")
    assert result.valid
    assert not result.has_differences
