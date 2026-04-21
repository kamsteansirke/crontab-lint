"""Tests for crontab_lint.rule_checker_formatter."""
from crontab_lint.rule_checker import RuleCheckResult, RuleViolation, check_expression, Rule
from crontab_lint.rule_checker_formatter import (
    format_violation,
    format_result,
    format_results,
    format_summary,
)


def _violation(name="test_rule", msg="something failed"):
    return RuleViolation(rule_name=name, message=msg)


def test_format_violation_contains_rule_name():
    v = _violation(name="my_rule")
    assert "my_rule" in format_violation(v)


def test_format_violation_contains_message():
    v = _violation(msg="the expression is bad")
    assert "the expression is bad" in format_violation(v)


def test_format_result_pass_shows_pass():
    result = RuleCheckResult(expression="30 6 * * *")
    text = format_result(result)
    assert "PASS" in text
    assert "30 6 * * *" in text


def test_format_result_fail_shows_fail():
    result = RuleCheckResult(
        expression="* * * * *",
        violations=[_violation()],
    )
    text = format_result(result)
    assert "FAIL" in text


def test_format_result_lists_violations():
    v = _violation(name="no_every_minute", msg="minute matches '*'")
    result = RuleCheckResult(expression="* * * * *", violations=[v])
    text = format_result(result)
    assert "no_every_minute" in text
    assert "minute matches" in text


def test_format_results_separates_blocks():
    r1 = RuleCheckResult(expression="30 6 * * *")
    r2 = RuleCheckResult(expression="* * * * *", violations=[_violation()])
    text = format_results([r1, r2])
    assert "30 6 * * *" in text
    assert "* * * * *" in text


def test_format_summary_counts():
    r1 = RuleCheckResult(expression="30 6 * * *")
    r2 = RuleCheckResult(expression="* * * * *", violations=[_violation()])
    text = format_summary([r1, r2])
    assert "2 checked" in text
    assert "1 passed" in text
    assert "1 failed" in text


def test_format_summary_all_pass():
    results = [RuleCheckResult(expression=e) for e in ["0 * * * *", "30 6 * * 1"]]
    text = format_summary(results)
    assert "2 passed" in text
    assert "0 failed" in text
