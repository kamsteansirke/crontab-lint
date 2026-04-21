"""Tests for expression_scorer_formatter."""
from crontab_lint.expression_scorer import score
from crontab_lint.expression_scorer_formatter import (
    format_score,
    format_scores,
    format_summary,
)


def test_format_score_contains_expression():
    result = score("0 6 * * *")
    output = format_score(result)
    assert "0 6 * * *" in output


def test_format_score_shows_grade():
    result = score("0 6 * * *")
    output = format_score(result)
    assert "Grade" in output


def test_format_score_shows_total():
    result = score("0 6 * * *")
    output = format_score(result)
    assert str(result.total) in output


def test_format_score_invalid_shows_invalid():
    result = score("bad expression")
    output = format_score(result)
    assert "INVALID" in output or "F" in output


def test_format_score_with_details_shows_categories():
    result = score("@daily")
    output = format_score(result, show_details=True)
    assert "validity" in output or "readability" in output or "specificity" in output


def test_format_score_no_details_hides_breakdown():
    result = score("@daily")
    output = format_score(result, show_details=False)
    assert "Breakdown" not in output


def test_format_scores_multiple_separated():
    results = [score("* * * * *"), score("@daily")]
    output = format_scores(results)
    assert "* * * * *" in output
    assert "@daily" in output


def test_format_summary_shows_count():
    results = [score("* * * * *"), score("@daily"), score("bad")]
    output = format_summary(results)
    assert "3" in output


def test_format_summary_shows_average():
    results = [score("0 6 * * *"), score("@weekly")]
    output = format_summary(results)
    assert "Average" in output


def test_format_summary_empty():
    output = format_summary([])
    assert "No expressions" in output
