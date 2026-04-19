"""Tests for the conflict detector module."""

import pytest
from crontab_lint.parser import parse
from crontab_lint.conflict_detector import detect_conflicts, _parse_field_values, _expressions_overlap


def _parsed(expr: str):
    return (expr, parse(expr))


def test_parse_field_wildcard():
    assert _parse_field_values("*", 0, 59) == set(range(0, 60))


def test_parse_field_specific():
    assert _parse_field_values("5", 0, 59) == {5}


def test_parse_field_range():
    assert _parse_field_values("1-3", 0, 59) == {1, 2, 3}


def test_parse_field_step():
    assert _parse_field_values("*/15", 0, 59) == {0, 15, 30, 45}


def test_parse_field_list():
    assert _parse_field_values("1,2,3", 0, 59) == {1, 2, 3}


def test_identical_expressions_conflict():
    a = _parsed("0 * * * *")
    b = _parsed("0 * * * *")
    report = detect_conflicts([a, b])
    assert report.has_conflicts
    assert len(report.conflicts) == 1


def test_non_overlapping_minutes_no_conflict():
    a = _parsed("0 * * * *")
    b = _parsed("30 * * * *")
    report = detect_conflicts([a, b])
    assert not report.has_conflicts


def test_non_overlapping_hours_no_conflict():
    a = _parsed("0 6 * * *")
    b = _parsed("0 12 * * *")
    report = detect_conflicts([a, b])
    assert not report.has_conflicts


def test_wildcard_overlaps_specific():
    a = _parsed("0 * * * *")
    b = _parsed("0 6 * * *")
    report = detect_conflicts([a, b])
    assert report.has_conflicts


def test_multiple_pairs():
    exprs = [
        _parsed("0 6 * * *"),
        _parsed("0 6 * * *"),
        _parsed("0 12 * * *"),
    ]
    report = detect_conflicts(exprs)
    assert len(report.conflicts) == 1
    assert report.conflicts[0].expression_a == "0 6 * * *"


def test_conflict_reason_message():
    a = _parsed("* * * * *")
    b = _parsed("* * * * *")
    report = detect_conflicts([a, b])
    assert "same time" in report.conflicts[0].reason


def test_empty_list_no_conflicts():
    report = detect_conflicts([])
    assert not report.has_conflicts
