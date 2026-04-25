"""Tests for expression_validator_report_formatter module."""
import pytest

from crontab_lint.expression_validator_report import (
    ValidationEntry,
    ValidationReport,
    validate_expressions,
)
from crontab_lint.expression_validator_report_formatter import (
    format_entry,
    format_report,
    format_summary,
)


def _valid_entry(expr="* * * * *"):
    return ValidationEntry(expression=expr, valid=True, explanation="Every minute.")


def _invalid_entry(expr="bad"):
    return ValidationEntry(expression=expr, valid=False, error="Parse error.")


def test_format_entry_valid_contains_expression():
    out = format_entry(_valid_entry("0 8 * * *"))
    assert "0 8 * * *" in out


def test_format_entry_valid_shows_check_mark():
    out = format_entry(_valid_entry())
    assert "✔" in out


def test_format_entry_valid_shows_explanation():
    out = format_entry(_valid_entry())
    assert "Every minute." in out


def test_format_entry_invalid_shows_cross():
    out = format_entry(_invalid_entry())
    assert "✘" in out


def test_format_entry_invalid_shows_error():
    out = format_entry(_invalid_entry())
    assert "Parse error." in out


def test_format_entry_with_index():
    out = format_entry(_valid_entry(), index=3)
    assert "3." in out


def test_format_entry_no_index_has_no_number_prefix():
    out = format_entry(_valid_entry())
    assert not out.startswith("1.")


def test_format_report_empty():
    report = ValidationReport(entries=[])
    out = format_report(report)
    assert "No expressions" in out


def test_format_report_contains_all_entries():
    report = validate_expressions(["* * * * *", "0 12 * * 5"])
    out = format_report(report)
    assert "* * * * *" in out
    assert "0 12 * * 5" in out


def test_format_summary_shows_counts():
    report = validate_expressions(["* * * * *", "bad-expr"])
    out = format_summary(report)
    assert "2" in out
    assert "1 valid" in out
    assert "1 invalid" in out
