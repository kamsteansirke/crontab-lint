"""Tests for crontab_lint.rule_checker."""
import pytest
from crontab_lint.rule_checker import (
    Rule,
    RuleViolation,
    RuleCheckResult,
    check_expression,
    check_many,
    _estimate_frequency_minutes,
)
from crontab_lint.parser import parse


EVERY_MINUTE_RULE = Rule(
    name="no_every_minute",
    description="Do not schedule every minute",
    forbidden_patterns={"minute": "*"},
)

FREQ_RULE = Rule(
    name="min_5_minutes",
    description="Must not run more often than every 5 minutes",
    max_frequency_minutes=5,
)


def test_check_expression_passes_clean():
    result = check_expression("30 6 * * 1", [EVERY_MINUTE_RULE])
    assert result.passed
    assert result.violations == []


def test_check_expression_detects_forbidden_pattern():
    result = check_expression("* * * * *", [EVERY_MINUTE_RULE])
    assert not result.passed
    assert len(result.violations) == 1
    assert result.violations[0].rule_name == "no_every_minute"
    assert "minute" in result.violations[0].message


def test_check_expression_frequency_violation():
    result = check_expression("*/2 * * * *", [FREQ_RULE])
    assert not result.passed
    assert result.violations[0].rule_name == "min_5_minutes"
    assert "2 minute" in result.violations[0].message


def test_check_expression_frequency_ok():
    result = check_expression("*/10 * * * *", [FREQ_RULE])
    assert result.passed


def test_check_expression_frequency_exactly_at_limit():
    """An expression at exactly the max_frequency_minutes boundary should pass."""
    result = check_expression("*/5 * * * *", [FREQ_RULE])
    assert result.passed


def test_check_expression_parse_error():
    result = check_expression("not a cron", [EVERY_MINUTE_RULE])
    assert not result.passed
    assert result.violations[0].rule_name == "parse"


def test_check_expression_multiple_rules():
    rules = [EVERY_MINUTE_RULE, FREQ_RULE]
    result = check_expression("* * * * *", rules)
    # Forbidden pattern fires; frequency (1 min) also fires
    rule_names = {v.rule_name for v in result.violations}
    assert "no_every_minute" in rule_names
    assert "min_5_minutes" in rule_names


def test_check_expression_no_rules():
    """Passing an empty rules list should always produce a passing result."""
    result = check_expression("* * * * *", [])
    assert result.passed
    assert result.violations == []


def test_check_many_returns_all_results():
    exprs = ["30 6 * * *", "* * * * *", "bad"]
    results = check_many(exprs, [EVERY_MINUTE_RULE])
    assert len(results) == 3
    assert results[0].passed
    assert not results[1].passed
    assert not results[2].passed


def test_check_many_empty_list():
    """check_many with an empty list of expressions should return an empty list."""
    results = check_many([], [EVERY_MINUTE_RULE])
    assert results == []


def test_check_many_preserves_order():
    """Results from check_many must correspond to inputs in the same order."""
    exprs = ["*/1 * * * *", "30 6 * * *", "*/3 * * * *", "0 0 * * *"]
    results = check_many(exprs, [FREQ_RULE])
    assert len(results) == 4
    assert not results[0].passed  # every 1 min — violation
    assert results[1].passed      # 06:30 daily — no frequency estimate, passes
    assert not results[2].passed  # every 3 min — violation
    assert results[3].passed      # midnight daily — no frequency estimate, passes


def test_estimate_frequency_wildcard():
    expr = parse("* * * * *")
    assert _estimate_frequency_minutes(expr) == 1


def test_estimate_frequency_step():
    expr = parse("*/15 * * * *")
    assert _estimate_frequency_minutes(expr) == 15


def test_estimate_frequency_specific_returns_none():
    expr = parse("30 6 * * *")
    assert _estimate_frequency_minutes(expr) is None
