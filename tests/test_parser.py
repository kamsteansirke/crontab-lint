"""Tests for crontab_lint.parser module."""

import pytest
from crontab_lint.parser import parse, validate_field, ParseError, CronExpression


def test_parse_basic_expression():
    expr = parse("0 12 * * 1")
    assert isinstance(expr, CronExpression)
    assert len(expr.fields) == 5
    assert expr.fields[0].raw == "0"
    assert expr.fields[1].raw == "12"
    assert expr.command is None


def test_parse_with_command():
    expr = parse("0 12 * * 1 /usr/bin/backup.sh")
    assert expr.command == "/usr/bin/backup.sh"


def test_parse_special_string_daily():
    expr = parse("@daily")
    assert expr.fields[0].raw == "0"
    assert expr.fields[1].raw == "0"


def test_parse_special_string_hourly():
    expr = parse("@hourly")
    assert expr.fields[1].raw == "*"


def test_parse_too_few_fields():
    with pytest.raises(ParseError):
        parse("0 12 *")


def test_validate_field_wildcard():
    expr = parse("* * * * *")
    for field in expr.fields:
        assert validate_field(field) == []


def test_validate_field_valid_value():
    expr = parse("30 6 * * *")
    assert validate_field(expr.fields[0]) == []
    assert validate_field(expr.fields[1]) == []


def test_validate_field_out_of_range():
    expr = parse("60 25 * * *")
    minute_errors = validate_field(expr.fields[0])
    hour_errors = validate_field(expr.fields[1])
    assert any("60" in e for e in minute_errors)
    assert any("25" in e for e in hour_errors)


def test_validate_field_valid_range():
    expr = parse("0-30 * * * *")
    assert validate_field(expr.fields[0]) == []


def test_validate_field_invalid_range_order():
    expr = parse("30-10 * * * *")
    errors = validate_field(expr.fields[0])
    assert any("start" in e for e in errors)


def test_validate_field_step():
    expr = parse("*/15 * * * *")
    assert validate_field(expr.fields[0]) == []


def test_validate_field_invalid_step_zero():
    expr = parse("*/0 * * * *")
    errors = validate_field(expr.fields[0])
    assert any("step" in e.lower() for e in errors)


def test_validate_field_list():
    expr = parse("0,15,30,45 * * * *")
    assert validate_field(expr.fields[0]) == []


def test_validate_field_unknown_token():
    expr = parse("abc * * * *")
    errors = validate_field(expr.fields[0])
    assert any("Unrecognized" in e for e in errors)
