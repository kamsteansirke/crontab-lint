"""Tests for crontab_lint.similarity and similarity_formatter."""
import pytest

from crontab_lint.similarity import (
    SimilarityResult,
    compare,
    rank_similar,
    _jaccard,
)
from crontab_lint.similarity_formatter import (
    format_result,
    format_ranking,
    format_summary,
)


# ---------------------------------------------------------------------------
# _jaccard
# ---------------------------------------------------------------------------

def test_jaccard_identical():
    assert _jaccard({1, 2, 3}, {1, 2, 3}) == 1.0


def test_jaccard_disjoint():
    assert _jaccard({1, 2}, {3, 4}) == 0.0


def test_jaccard_partial():
    score = _jaccard({1, 2, 3}, {2, 3, 4})
    assert 0.0 < score < 1.0


def test_jaccard_both_empty():
    assert _jaccard(set(), set()) == 1.0


# ---------------------------------------------------------------------------
# compare
# ---------------------------------------------------------------------------

def test_compare_identical_expressions():
    result = compare("0 9 * * 1", "0 9 * * 1")
    assert result.is_valid
    assert result.score == 1.0


def test_compare_completely_different():
    result = compare("0 9 1 1 1", "30 23 31 12 5")
    assert result.is_valid
    assert result.score < 0.5


def test_compare_wildcard_vs_specific():
    result = compare("* * * * *", "0 9 * * 1")
    assert result.is_valid
    # wildcards cover everything so overlap with any specific value exists
    assert 0.0 < result.score <= 1.0


def test_compare_returns_five_field_scores():
    result = compare("0 9 * * 1", "0 10 * * 1")
    assert result.is_valid
    assert len(result.field_scores) == 5


def test_compare_invalid_expression_a():
    result = compare("not_a_cron", "0 9 * * 1")
    assert not result.is_valid
    assert result.score == 0.0
    assert result.error


def test_compare_invalid_expression_b():
    result = compare("0 9 * * 1", "bad")
    assert not result.is_valid


def test_compare_special_strings():
    result = compare("@daily", "@daily")
    assert result.is_valid
    assert result.score == 1.0


# ---------------------------------------------------------------------------
# rank_similar
# ---------------------------------------------------------------------------

def test_rank_similar_returns_top_n():
    candidates = ["0 9 * * 1", "0 10 * * 1", "0 9 * * 2", "30 9 * * 1"]
    ranking = rank_similar("0 9 * * 1", candidates, top_n=2)
    assert len(ranking) == 2


def test_rank_similar_excludes_target():
    candidates = ["0 9 * * 1", "0 10 * * 1"]
    ranking = rank_similar("0 9 * * 1", candidates)
    expressions = [e for e, _ in ranking]
    assert "0 9 * * 1" not in expressions


def test_rank_similar_sorted_descending():
    candidates = ["0 9 * * 1", "0 10 * * 1", "30 23 31 12 5"]
    ranking = rank_similar("0 9 * * 1", candidates)
    scores = [s for _, s in ranking]
    assert scores == sorted(scores, reverse=True)


# ---------------------------------------------------------------------------
# formatter
# ---------------------------------------------------------------------------

def test_format_result_contains_expressions():
    result = compare("0 9 * * 1", "0 10 * * 1")
    text = format_result(result)
    assert "0 9 * * 1" in text
    assert "0 10 * * 1" in text


def test_format_result_shows_similarity_percentage():
    result = compare("0 9 * * 1", "0 9 * * 1")
    text = format_result(result)
    assert "100%" in text


def test_format_result_invalid_shows_error():
    result = compare("bad", "0 9 * * 1")
    text = format_result(result)
    assert "ERROR" in text


def test_format_result_show_fields():
    result = compare("0 9 * * 1", "0 9 * * 1")
    text = format_result(result, show_fields=True)
    assert "minute" in text


def test_format_ranking_contains_candidates():
    candidates = ["0 10 * * 1", "30 9 * * 1"]
    ranking = rank_similar("0 9 * * 1", candidates)
    text = format_ranking("0 9 * * 1", ranking)
    for expr, _ in ranking:
        assert expr in text


def test_format_ranking_empty():
    text = format_ranking("0 9 * * 1", [])
    assert "No candidates" in text


def test_format_summary_valid():
    results = [compare("0 9 * * 1", "0 9 * * 1"), compare("* * * * *", "0 9 * * 1")]
    text = format_summary(results)
    assert "2 comparison(s)" in text


def test_format_summary_with_errors():
    results = [compare("bad", "0 9 * * 1")]
    text = format_summary(results)
    assert "error" in text.lower()
