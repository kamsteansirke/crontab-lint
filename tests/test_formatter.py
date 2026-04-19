"""Tests for the formatter module."""

import pytest
from crontab_lint.formatter import LintResult, format_result, format_results


def _make_valid(expression="* * * * *", explanation="every minute of every hour"):
    return LintResult(
        expression=expression,
        command="/usr/bin/backup",
        valid=True,
        explanation=explanation,
    )


def _make_invalid(expression="60 * * * *"):
    return LintResult(
        expression=expression,
        command=None,
        valid=False,
        errors=["minute value 60 out of range 0-59"],
    )


def test_format_valid_result_contains_expression():
    result = _make_valid()
    output = format_result(result, color=False)
    assert "* * * * *" in output


def test_format_valid_result_shows_valid():
    output = format_result(_make_valid(), color=False)
    assert "VALID" in output


def test_format_invalid_result_shows_invalid():
    output = format_result(_make_invalid(), color=False)
    assert "INVALID" in output


def test_format_result_shows_error():
    output = format_result(_make_invalid(), color=False)
    assert "ERROR" in output
    assert "minute value 60" in output


def test_format_result_shows_explanation():
    output = format_result(_make_valid(), color=False)
    assert "every minute" in output


def test_format_result_shows_command():
    output = format_result(_make_valid(), color=False)
    assert "/usr/bin/backup" in output


def test_format_result_with_warning():
    r = LintResult(expression="* * * * *", command=None, valid=True,
                   warnings=["runs every minute, may cause high load"])
    output = format_result(r, color=False)
    assert "WARN" in output
    assert "high load" in output


def test_format_multiple_results():
    results = [_make_valid(), _make_invalid()]
    output = format_results(results, color=False)
    assert "VALID" in output
    assert "INVALID" in output
    assert output.count("\n\n") >= 1
