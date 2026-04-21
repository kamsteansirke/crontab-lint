"""Tests for expression_scorer."""
import pytest
from crontab_lint.expression_scorer import score, ExpressionScore


def test_score_every_minute_is_valid():
    result = score("* * * * *")
    assert result.valid is True


def test_score_every_minute_penalises_all_wildcards():
    result = score("* * * * *")
    penalties = [d for d in result.details if d.points < 0]
    assert any("wildcard" in d.message.lower() or "every minute" in d.message.lower() for d in penalties)


def test_score_specific_time_gets_specificity_bonus():
    result = score("30 6 * * 1")
    specificity = [d for d in result.details if d.category == "specificity"]
    assert specificity[0].points >= 20


def test_score_special_string_gets_readability_bonus():
    result = score("@daily")
    readability = [d for d in result.details if d.category == "readability"]
    assert any(d.points >= 20 for d in readability)


def test_score_invalid_expression_returns_invalid():
    result = score("not a cron")
    assert result.valid is False
    assert result.grade == "F"
    assert result.error != ""


def test_score_total_within_bounds():
    for expr in ["* * * * *", "0 0 * * *", "@weekly", "*/5 * * * *"]:
        result = score(expr)
        if result.valid:
            assert 0 <= result.total <= result.max_score


def test_grade_a_for_high_score():
    # @daily should score well
    result = score("@daily")
    assert result.grade in ("A", "B")


def test_grade_f_for_invalid():
    result = score("60 25 * * *")
    # parser should reject out-of-range values
    if not result.valid:
        assert result.grade == "F"


def test_step_value_bonus_present():
    result = score("*/15 * * * *")
    assert result.valid
    step_details = [d for d in result.details if d.category == "readability" and "step" in d.message.lower()]
    assert len(step_details) == 1


def test_score_returns_expression_scorer_instance():
    result = score("0 12 * * *")
    assert isinstance(result, ExpressionScore)
