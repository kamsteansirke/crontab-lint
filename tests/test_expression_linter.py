"""Tests for expression_linter and expression_linter_formatter."""
import pytest

from crontab_lint.expression_linter import lint, AggregateLintResult, LintIssue
from crontab_lint.expression_linter_formatter import (
    format_issue,
    format_result,
    format_results,
    format_summary,
)
from crontab_lint.rule_checker import Rule
from crontab_lint.env_validator import EnvConstraint


# ---------------------------------------------------------------------------
# lint()
# ---------------------------------------------------------------------------

def test_lint_valid_expression_is_valid():
    result = lint("0 9 * * 1")
    assert result.is_valid is True


def test_lint_invalid_expression_is_not_valid():
    result = lint("not a cron")
    assert result.is_valid is False


def test_lint_invalid_has_parse_error_issue():
    result = lint("not a cron")
    assert any(i.category == "parse" and i.severity == "error" for i in result.issues)


def test_lint_valid_has_explanation():
    result = lint("0 9 * * 1")
    assert result.explanation is not None
    assert len(result.explanation) > 0


def test_lint_invalid_explanation_is_none():
    result = lint("bad")
    assert result.explanation is None


def test_lint_score_populated_for_valid():
    result = lint("0 9 * * 1")
    assert result.score is not None


def test_lint_score_none_for_invalid():
    result = lint("bad")
    assert result.score is None


def test_lint_with_rule_violation():
    rule = Rule(name="no-every-minute", pattern="\\* \\* \\* \\* \\*", message="Too frequent")
    result = lint("* * * * *", rules=[rule])
    assert result.rule_result is not None
    assert any(i.category == "rule" for i in result.issues)


def test_lint_with_env_constraint_violation():
    constraint = EnvConstraint(field="minute", allowed_values=[0, 30])
    result = lint("15 * * * *", constraints=[constraint])
    assert result.env_result is not None
    assert any(i.category == "env" for i in result.issues)


def test_lint_has_errors_true_for_invalid():
    result = lint("bad")
    assert result.has_errors is True


def test_lint_has_errors_false_for_valid_no_rules():
    result = lint("0 9 * * 1")
    assert result.has_errors is False


# ---------------------------------------------------------------------------
# format_issue()
# ---------------------------------------------------------------------------

def test_format_issue_contains_category():
    issue = LintIssue(category="parse", message="bad token", severity="error")
    assert "parse" in format_issue(issue)


def test_format_issue_contains_message():
    issue = LintIssue(category="rule", message="Too frequent", severity="warning")
    assert "Too frequent" in format_issue(issue)


def test_format_issue_shows_severity():
    issue = LintIssue(category="env", message="out of range", severity="error")
    text = format_issue(issue)
    assert "ERROR" in text


# ---------------------------------------------------------------------------
# format_result()
# ---------------------------------------------------------------------------

def test_format_result_contains_expression():
    result = lint("0 9 * * 1")
    text = format_result(result)
    assert "0 9 * * 1" in text


def test_format_result_shows_valid():
    result = lint("0 9 * * 1")
    assert "VALID" in format_result(result)


def test_format_result_shows_invalid():
    result = lint("bad")
    assert "INVALID" in format_result(result)


def test_format_result_shows_score_by_default():
    result = lint("0 9 * * 1")
    assert "Score" in format_result(result)


def test_format_result_hides_score_when_flag_false():
    result = lint("0 9 * * 1")
    assert "Score" not in format_result(result, show_score=False)


# ---------------------------------------------------------------------------
# format_summary()
# ---------------------------------------------------------------------------

def test_format_summary_shows_totals():
    results = [lint("0 9 * * 1"), lint("bad")]
    text = format_summary(results)
    assert "2" in text
    assert "1" in text
