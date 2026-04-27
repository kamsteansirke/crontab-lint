"""Tests for crontab_lint.expression_formatter."""

import pytest

from crontab_lint.expression_formatter import (
    FieldRow,
    FormattedExpression,
    format_expression,
    render_table,
)


# ---------------------------------------------------------------------------
# format_expression
# ---------------------------------------------------------------------------

def test_format_valid_expression_is_valid():
    result = format_expression("0 9 * * 1")
    assert result.is_valid is True


def test_format_valid_expression_has_no_error():
    result = format_expression("0 9 * * 1")
    assert result.error is None


def test_format_valid_expression_has_five_fields():
    result = format_expression("*/5 * * * *")
    assert len(result.fields) == 5


def test_format_valid_expression_field_names():
    result = format_expression("0 0 1 1 *")
    names = [f.name for f in result.fields]
    assert "Minute" in names
    assert "Hour" in names
    assert "Month" in names


def test_format_valid_expression_field_values():
    result = format_expression("30 6 * * *")
    values = {f.name: f.value for f in result.fields}
    assert values["Minute"] == "30"
    assert values["Hour"] == "6"


def test_format_valid_expression_has_explanation():
    result = format_expression("0 0 * * *")
    assert result.explanation is not None
    assert len(result.explanation) > 0


def test_format_valid_expression_ok_property():
    result = format_expression("* * * * *")
    assert result.ok is True


def test_format_invalid_expression_is_not_valid():
    result = format_expression("not a cron")
    assert result.is_valid is False


def test_format_invalid_expression_has_error():
    result = format_expression("99 99 99 99 99")
    assert result.error is not None


def test_format_invalid_expression_has_no_fields():
    result = format_expression("bad expression")
    assert result.fields == []


def test_format_invalid_expression_explanation_is_none():
    result = format_expression("bad expression")
    assert result.explanation is None


def test_format_expression_stores_raw():
    expr = "0 12 * * 5"
    result = format_expression(expr)
    assert result.raw == expr


# ---------------------------------------------------------------------------
# render_table
# ---------------------------------------------------------------------------

def test_render_table_valid_contains_expression():
    fmt = format_expression("0 9 * * 1")
    table = render_table(fmt)
    assert "0 9 * * 1" in table


def test_render_table_valid_shows_status():
    fmt = format_expression("*/15 * * * *")
    table = render_table(fmt)
    assert "valid" in table.lower()


def test_render_table_invalid_shows_invalid():
    fmt = format_expression("not valid at all")
    table = render_table(fmt)
    assert "INVALID" in table


def test_render_table_invalid_shows_error_message():
    fmt = format_expression("not valid at all")
    table = render_table(fmt)
    assert fmt.error in table


def test_render_table_valid_shows_field_values():
    fmt = format_expression("30 6 * * *")
    table = render_table(fmt)
    assert "30" in table
    assert "6" in table
