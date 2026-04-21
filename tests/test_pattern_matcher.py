"""Tests for crontab_lint.pattern_matcher."""
from __future__ import annotations

import pytest

from crontab_lint.pattern_matcher import MatchResult, best_match, match


def test_match_returns_list():
    results = match("daily")
    assert isinstance(results, list)


def test_match_daily_contains_daily_expression():
    results = match("daily")
    expressions = [r.expression for r in results]
    assert any("0 0" in e or "daily" in e for e in expressions)


def test_match_hourly_contains_hourly_expression():
    results = match("hourly")
    expressions = [r.expression for r in results]
    assert any("hourly" in e or "0 *" in e for e in expressions)


def test_match_unknown_query_returns_empty():
    results = match("xyzzy frobnicator")
    assert results == []


def test_match_top_n_limits_results():
    results = match("daily midnight backup", top_n=2)
    assert len(results) <= 2


def test_match_result_has_explanation():
    results = match("midnight")
    for r in results:
        assert r.explanation != ""


def test_match_score_between_zero_and_one():
    results = match("morning daily")
    for r in results:
        assert 0.0 <= r.score <= 1.0


def test_best_match_returns_single_result():
    result = best_match("hourly")
    assert result is not None
    assert isinstance(result, MatchResult)


def test_best_match_unknown_returns_none():
    result = best_match("totally unknown gibberish")
    assert result is None


def test_match_results_are_sorted_by_score_descending():
    results = match("daily midnight")
    scores = [r.score for r in results]
    assert scores == sorted(scores, reverse=True)


def test_match_weekly_expression_present():
    results = match("weekly")
    expressions = [r.expression for r in results]
    assert any("weekly" in e or "* * 0" in e or "0 0" in e for e in expressions)
