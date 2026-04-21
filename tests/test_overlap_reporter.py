"""Tests for crontab_lint.overlap_reporter."""

import pytest
from crontab_lint.overlap_reporter import (
    OverlapEntry,
    OverlapReport,
    build_overlap_report,
    format_overlap_report,
)


def test_no_expressions_returns_empty_report():
    report = build_overlap_report([])
    assert not report.has_overlaps
    assert report.count == 0


def test_single_expression_no_overlap():
    report = build_overlap_report(["0 * * * *"])
    assert not report.has_overlaps


def test_identical_expressions_overlap():
    report = build_overlap_report(["0 9 * * 1", "0 9 * * 1"])
    assert report.has_overlaps
    assert report.count == 1


def test_non_overlapping_expressions():
    # Different hours: 9 AM vs 5 PM
    report = build_overlap_report(["0 9 * * *", "0 17 * * *"])
    assert not report.has_overlaps


def test_overlap_entry_has_both_expressions():
    report = build_overlap_report(["* * * * *", "* * * * *"])
    assert report.has_overlaps
    entry = report.entries[0]
    assert entry.expression_a == "* * * * *"
    assert entry.expression_b == "* * * * *"


def test_overlap_entry_has_explanations():
    report = build_overlap_report(["0 9 * * 1", "0 9 * * 1"])
    assert report.has_overlaps
    entry = report.entries[0]
    assert len(entry.explanation_a) > 0
    assert len(entry.explanation_b) > 0


def test_invalid_expression_skipped():
    report = build_overlap_report(["not-a-cron", "* * * * *"])
    # Invalid expression should be skipped, no crash
    assert report.count == 0


def test_multiple_pairs_detected():
    exprs = ["* * * * *", "* * * * *", "* * * * *"]
    report = build_overlap_report(exprs)
    # 3 pairs: (0,1), (0,2), (1,2)
    assert report.count == 3


def test_format_no_overlaps():
    report = OverlapReport()
    output = format_overlap_report(report)
    assert "No overlapping" in output


def test_format_with_overlaps_contains_expressions():
    report = build_overlap_report(["0 9 * * 1", "0 9 * * 1"])
    output = format_overlap_report(report)
    assert "0 9 * * 1" in output


def test_format_with_overlaps_shows_count():
    report = build_overlap_report(["* * * * *", "* * * * *"])
    output = format_overlap_report(report)
    assert "1" in output


def test_format_shows_overlapping_fields():
    report = build_overlap_report(["0 9 * * 1", "0 9 * * 1"])
    output = format_overlap_report(report)
    assert "Overlapping fields" in output
