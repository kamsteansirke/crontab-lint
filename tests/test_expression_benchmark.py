"""Tests for expression_benchmark module."""
import pytest
from crontab_lint.expression_benchmark import benchmark, BenchmarkReport, BenchmarkEntry


EVERY_MINUTE = "* * * * *"
ONCE_DAILY = "0 0 * * *"
INVALID = "invalid expression"


def test_benchmark_empty_list_returns_empty_report():
    report = benchmark([])
    assert isinstance(report, BenchmarkReport)
    assert report.total == 0


def test_benchmark_skips_blank_lines():
    report = benchmark(["", "   ", "\t"])
    assert report.total == 0


def test_benchmark_skips_comment_lines():
    report = benchmark(["# this is a comment", EVERY_MINUTE])
    assert report.total == 1


def test_benchmark_valid_expression_is_valid():
    report = benchmark([EVERY_MINUTE])
    assert report.valid_count == 1
    assert report.invalid_count == 0


def test_benchmark_invalid_expression_is_invalid():
    report = benchmark([INVALID])
    assert report.invalid_count == 1
    assert report.valid_count == 0


def test_benchmark_invalid_entry_has_error():
    report = benchmark([INVALID])
    entry = report.entries[0]
    assert entry.error is not None
    assert len(entry.error) > 0


def test_benchmark_valid_entry_has_no_error():
    report = benchmark([EVERY_MINUTE])
    entry = report.entries[0]
    assert entry.error is None


def test_benchmark_every_minute_runs_per_day():
    report = benchmark([EVERY_MINUTE])
    entry = report.entries[0]
    assert entry.runs_per_day == pytest.approx(1440.0, rel=0.01)


def test_benchmark_once_daily_runs_per_day():
    report = benchmark([ONCE_DAILY])
    entry = report.entries[0]
    assert entry.runs_per_day == pytest.approx(1.0, rel=0.01)


def test_benchmark_ranking_most_frequent_is_rank_one():
    report = benchmark([ONCE_DAILY, EVERY_MINUTE])
    ranked = {e.expression: e.rank for e in report.entries if e.is_valid}
    assert ranked[EVERY_MINUTE] == 1
    assert ranked[ONCE_DAILY] == 2


def test_benchmark_invalid_entry_has_zero_runs():
    report = benchmark([INVALID])
    assert report.entries[0].runs_per_day == 0.0


def test_benchmark_total_counts_all_entries():
    report = benchmark([EVERY_MINUTE, ONCE_DAILY, INVALID])
    assert report.total == 3


def test_benchmark_entry_has_cost_level():
    report = benchmark([EVERY_MINUTE])
    assert report.entries[0].cost_level != ""


def test_benchmark_entry_has_frequency_category():
    report = benchmark([EVERY_MINUTE])
    assert report.entries[0].frequency_category != ""
