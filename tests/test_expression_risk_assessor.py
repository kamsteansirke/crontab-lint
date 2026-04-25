"""Tests for expression_risk_assessor."""
import pytest
from crontab_lint.expression_risk_assessor import (
    assess,
    assess_many,
    RiskAssessment,
    RISK_LOW,
    RISK_MEDIUM,
    RISK_HIGH,
    RISK_CRITICAL,
)


def test_assess_returns_risk_assessment():
    result = assess("0 9 * * 1")
    assert isinstance(result, RiskAssessment)


def test_assess_invalid_expression_is_not_valid():
    result = assess("not a cron")
    assert result.is_valid is False


def test_assess_invalid_expression_has_error():
    result = assess("not a cron")
    assert result.error is not None and len(result.error) > 0


def test_assess_invalid_expression_risk_level_is_high():
    result = assess("not a cron")
    assert result.risk_level == RISK_HIGH


def test_assess_every_minute_is_valid():
    result = assess("* * * * *")
    assert result.is_valid is True


def test_assess_every_minute_is_critical():
    result = assess("* * * * *")
    assert result.risk_level == RISK_CRITICAL


def test_assess_every_minute_score_is_high():
    result = assess("* * * * *")
    assert result.risk_score >= 60


def test_assess_every_minute_has_every_minute_factor():
    result = assess("* * * * *")
    names = [f.name for f in result.factors]
    assert "every_minute" in names


def test_assess_once_daily_is_low_risk():
    result = assess("0 3 * * *")
    assert result.risk_level == RISK_LOW


def test_assess_once_daily_has_no_factors():
    result = assess("0 3 * * *")
    assert result.factors == []


def test_assess_has_risks_false_when_no_factors():
    result = assess("0 3 * * *")
    assert result.has_risks is False


def test_assess_has_risks_true_when_factors_present():
    result = assess("* * * * *")
    assert result.has_risks is True


def test_assess_redundant_step_detected():
    result = assess("*/1 * * * *")
    names = [f.name for f in result.factors]
    assert "redundant_step" in names


def test_assess_reboot_trigger_detected():
    result = assess("@reboot /usr/bin/backup.sh")
    names = [f.name for f in result.factors]
    assert "reboot_trigger" in names


def test_assess_many_returns_list():
    results = assess_many(["* * * * *", "0 9 * * 1"])
    assert len(results) == 2


def test_assess_many_preserves_order():
    exprs = ["0 1 * * *", "0 2 * * *", "0 3 * * *"]
    results = assess_many(exprs)
    assert [r.expression for r in results] == exprs


def test_assess_score_is_zero_for_clean_expression():
    result = assess("0 0 1 1 *")
    assert result.risk_score == 0
