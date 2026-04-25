"""Tests for expression_risk_assessor_formatter."""
import pytest
from crontab_lint.expression_risk_assessor import assess, assess_many
from crontab_lint.expression_risk_assessor_formatter import (
    format_assessment,
    format_assessments,
    format_summary,
)


def _valid():
    return assess("0 9 * * 1")


def _invalid():
    return assess("bad expression!!")


def _critical():
    return assess("* * * * *")


def test_format_assessment_contains_expression():
    result = format_assessment(_valid())
    assert "0 9 * * 1" in result


def test_format_assessment_shows_risk_level():
    result = format_assessment(_valid())
    assert "LOW" in result or "MEDIUM" in result or "HIGH" in result or "CRITICAL" in result


def test_format_assessment_invalid_shows_invalid():
    result = format_assessment(_invalid())
    assert "INVALID" in result


def test_format_assessment_invalid_shows_error():
    a = _invalid()
    result = format_assessment(a)
    assert a.error in result


def test_format_assessment_critical_shows_critical():
    result = format_assessment(_critical())
    assert "CRITICAL" in result


def test_format_assessment_with_index():
    result = format_assessment(_valid(), index=3)
    assert "[3]" in result


def test_format_assessment_no_index_no_bracket():
    result = format_assessment(_valid(), index=None)
    assert "[" not in result or "[" not in result.split("\n")[0]


def test_format_assessment_factors_listed():
    result = format_assessment(_critical())
    assert "every_minute" in result


def test_format_assessment_no_factors_shows_none():
    result = format_assessment(_valid())
    assert "none" in result


def test_format_assessments_empty_returns_message():
    result = format_assessments([])
    assert "No expressions" in result


def test_format_assessments_multiple_contains_all():
    assessments = assess_many(["0 9 * * 1", "* * * * *"])
    result = format_assessments(assessments)
    assert "0 9 * * 1" in result
    assert "* * * * *" in result


def test_format_assessments_indexed():
    assessments = assess_many(["0 9 * * 1", "0 3 * * *"])
    result = format_assessments(assessments)
    assert "[1]" in result
    assert "[2]" in result


def test_format_summary_empty():
    result = format_summary([])
    assert "0" in result


def test_format_summary_shows_total():
    assessments = assess_many(["0 9 * * 1", "* * * * *"])
    result = format_summary(assessments)
    assert "2" in result


def test_format_summary_shows_critical_count():
    assessments = assess_many(["* * * * *"])
    result = format_summary(assessments)
    assert "Critical" in result or "critical" in result
