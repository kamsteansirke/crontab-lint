"""Tests for expression_benchmark_formatter module."""
from crontab_lint.expression_benchmark import benchmark
from crontab_lint.expression_benchmark_formatter import (
    format_entry,
    format_report,
    format_summary,
)

EVERY_MINUTE = "* * * * *"
ONCE_DAILY = "0 0 * * *"
INVALID = "not a cron"


def _report(*expressions):
    return benchmark(list(expressions))


def test_format_entry_valid_contains_expression():
    report = _report(EVERY_MINUTE)
    result = format_entry(report.entries[0])
    assert EVERY_MINUTE in result


def test_format_entry_valid_contains_cost_level():
    report = _report(EVERY_MINUTE)
    result = format_entry(report.entries[0])
    assert "cost=" in result


def test_format_entry_valid_contains_runs_per_day():
    report = _report(EVERY_MINUTE)
    result = format_entry(report.entries[0])
    assert "runs/day=" in result


def test_format_entry_invalid_shows_invalid():
    report = _report(INVALID)
    result = format_entry(report.entries[0])
    assert "INVALID" in result


def test_format_entry_invalid_contains_expression():
    report = _report(INVALID)
    result = format_entry(report.entries[0])
    assert INVALID in result


def test_format_entry_with_index():
    report = _report(EVERY_MINUTE)
    result = format_entry(report.entries[0], index=3)
    assert result.startswith("3.")


def test_format_report_empty_returns_message():
    report = _report()
    result = format_report(report)
    assert "No expressions" in result


def test_format_report_contains_expression():
    report = _report(EVERY_MINUTE)
    result = format_report(report)
    assert EVERY_MINUTE in result


def test_format_report_contains_header():
    report = _report(EVERY_MINUTE)
    result = format_report(report)
    assert "Benchmark" in result


def test_format_summary_shows_total():
    report = _report(EVERY_MINUTE, ONCE_DAILY)
    result = format_summary(report)
    assert "2" in result


def test_format_summary_shows_valid_count():
    report = _report(EVERY_MINUTE, INVALID)
    result = format_summary(report)
    assert "Valid" in result


def test_format_summary_shows_most_frequent():
    report = _report(EVERY_MINUTE, ONCE_DAILY)
    result = format_summary(report)
    assert EVERY_MINUTE in result
