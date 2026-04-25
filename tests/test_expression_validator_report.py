"""Tests for expression_validator_report module."""
import pytest

from crontab_lint.expression_validator_report import (
    ValidationEntry,
    ValidationReport,
    validate_expressions,
)


def test_validate_empty_list_returns_empty_report():
    report = validate_expressions([])
    assert report.total == 0
    assert report.all_valid


def test_validate_skips_blank_lines():
    report = validate_expressions(["", "   ", "\n"])
    assert report.total == 0


def test_validate_skips_comment_lines():
    report = validate_expressions(["# this is a comment", "#another"])
    assert report.total == 0


def test_validate_single_valid_expression():
    report = validate_expressions(["* * * * *"])
    assert report.total == 1
    assert report.valid_count == 1
    assert report.invalid_count == 0
    assert report.all_valid


def test_validate_entry_has_explanation():
    report = validate_expressions(["0 9 * * 1"])
    entry = report.entries[0]
    assert entry.valid
    assert entry.explanation is not None
    assert len(entry.explanation) > 0


def test_validate_invalid_expression():
    report = validate_expressions(["invalid expression here"])
    assert report.total == 1
    assert report.invalid_count == 1
    assert not report.all_valid
    entry = report.entries[0]
    assert not entry.valid
    assert entry.error is not None


def test_validate_mixed_expressions():
    report = validate_expressions(["0 6 * * *", "not-a-cron", "@daily"])
    assert report.total == 3
    assert report.valid_count == 2
    assert report.invalid_count == 1


def test_validation_report_counts():
    r = ValidationReport(entries=[
        ValidationEntry(expression="a", valid=True),
        ValidationEntry(expression="b", valid=False),
        ValidationEntry(expression="c", valid=True),
    ])
    assert r.total == 3
    assert r.valid_count == 2
    assert r.invalid_count == 1
    assert not r.all_valid
