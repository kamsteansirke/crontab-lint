"""Tests for the explainer module."""

import pytest
from crontab_lint.parser import parse
from crontab_lint.explainer import explain


def test_explain_every_minute():
    expr = parse("* * * * *")
    assert "every minute" in explain(expr)


def test_explain_specific_time():
    expr = parse("30 8 * * *")
    result = explain(expr)
    assert "30" in result
    assert "8" in result


def test_explain_day_of_week():
    expr = parse("0 9 * * 1")
    result = explain(expr)
    assert "Monday" in result


def test_explain_month():
    expr = parse("0 0 1 6 *")
    result = explain(expr)
    assert "June" in result


def test_explain_day_of_month():
    expr = parse("0 0 15 * *")
    result = explain(expr)
    assert "15th" in result


def test_explain_step():
    expr = parse("*/15 * * * *")
    result = explain(expr)
    assert "every 15" in result


def test_explain_special_daily():
    expr = parse("@daily")
    assert explain(expr) == "Once a day, at midnight"


def test_explain_special_hourly():
    expr = parse("@hourly")
    assert explain(expr) == "Once an hour, at the start of the hour"


def test_explain_special_reboot():
    expr = parse("@reboot")
    assert explain(expr) == "At system reboot"


def test_explain_special_yearly():
    expr = parse("@yearly")
    assert "January" in explain(expr)
