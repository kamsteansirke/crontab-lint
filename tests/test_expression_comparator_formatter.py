"""Tests for expression_comparator_formatter module."""
import pytest
from crontab_lint.expression_comparator import compare
from crontab_lint.expression_comparator_formatter import (
    format_comparison,
    format_comparisons,
    format_summary,
    format_field_diff,
)
from crontab_lint.expression_comparator import FieldDiff


def test_format_comparison_contains_left_expression():
    result = compare("0 9 * * *", "0 10 * * *")
    output = format_comparison(result)
    assert "0 9 * * *" in output


def test_format_comparison_contains_right_expression():
    result = compare("0 9 * * *", "0 10 * * *")
    output = format_comparison(result)
    assert "0 10 * * *" in output


def test_format_comparison_identical_says_identical():
    result = compare("0 9 * * *", "0 9 * * *")
    output = format_comparison(result)
    assert "identical" in output.lower()


def test_format_comparison_different_shows_changed_fields():
    result = compare("0 9 * * *", "0 10 * * *")
    output = format_comparison(result)
    assert "hour" in output


def test_format_comparison_invalid_shows_error():
    result = compare("notvalid", "0 9 * * *")
    output = format_comparison(result)
    assert "ERROR" in output or "error" in output.lower()


def test_format_comparison_shows_explanation():
    result = compare("0 9 * * *", "0 10 * * *")
    output = format_comparison(result)
    assert "explanation" in output.lower()


def test_format_field_diff_changed_has_arrow():
    diff = FieldDiff(name="minute", left="0", right="30", changed=True)
    output = format_field_diff(diff)
    assert "->" in output


def test_format_field_diff_unchanged_no_arrow():
    diff = FieldDiff(name="hour", left="9", right="9", changed=False)
    output = format_field_diff(diff)
    assert "->" not in output


def test_format_comparisons_multiple_results():
    results = [
        compare("0 9 * * *", "0 10 * * *"),
        compare("* * * * *", "* * * * *"),
    ]
    output = format_comparisons(results)
    assert "0 9 * * *" in output
    assert "* * * * *" in output


def test_format_summary_counts():
    results = [
        compare("0 9 * * *", "0 9 * * *"),
        compare("0 9 * * *", "0 10 * * *"),
        compare("bad", "also bad"),
    ]
    output = format_summary(results)
    assert "3" in output
    assert "Identical" in output
    assert "Different" in output
    assert "Errors" in output
