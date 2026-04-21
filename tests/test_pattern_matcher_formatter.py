"""Tests for crontab_lint.pattern_matcher_formatter."""
from __future__ import annotations

import pytest

from crontab_lint.pattern_matcher import MatchResult
from crontab_lint.pattern_matcher_formatter import (
    _bar,
    format_match,
    format_matches,
    format_summary,
)


def _result(expr="0 0 * * *", explanation="At midnight", score=0.8) -> MatchResult:
    return MatchResult(expression=expr, explanation=explanation, score=score)


def test_format_match_contains_expression():
    r = _result()
    assert "0 0 * * *" in format_match(r)


def test_format_match_contains_explanation():
    r = _result()
    assert "At midnight" in format_match(r)


def test_format_match_contains_score():
    r = _result(score=0.75)
    out = format_match(r)
    assert "75%" in out


def test_format_match_with_index():
    r = _result()
    out = format_match(r, index=3)
    assert out.startswith("3.")


def test_format_match_without_index_no_number_prefix():
    r = _result()
    out = format_match(r, index=None)
    assert not out.startswith("1.")


def test_format_matches_empty_returns_no_matches_message():
    out = format_matches([], query="foobar")
    assert "No matches" in out
    assert "foobar" in out


def test_format_matches_nonempty_contains_all_expressions():
    results = [_result("0 0 * * *"), _result("@daily", score=0.6)]
    out = format_matches(results, query="daily")
    assert "0 0 * * *" in out
    assert "@daily" in out


def test_format_matches_includes_query():
    results = [_result()]
    out = format_matches(results, query="midnight")
    assert "midnight" in out


def test_format_summary_no_results():
    out = format_summary([])
    assert "No" in out


def test_format_summary_shows_count_and_best():
    results = [_result(score=0.5), _result("@daily", score=0.9)]
    out = format_summary(results)
    assert "2" in out
    assert "@daily" in out


def test_bar_full():
    assert _bar(1.0) == "[##########]"


def test_bar_empty():
    assert _bar(0.0) == "[----------]"


def test_bar_half():
    assert _bar(0.5) == "[#####-----]"
