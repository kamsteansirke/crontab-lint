"""Tests for expression_recommender and expression_recommender_formatter."""
import pytest

from crontab_lint.expression_recommender import (
    Recommendation,
    RecommendationResult,
    recommend,
)
from crontab_lint.expression_recommender_formatter import (
    format_recommendation,
    format_result,
    format_summary,
)


# ---------------------------------------------------------------------------
# recommend()
# ---------------------------------------------------------------------------

def test_recommend_empty_query_returns_error():
    result = recommend("")
    assert result.error is not None
    assert not result.has_results


def test_recommend_whitespace_only_returns_error():
    result = recommend("   ")
    assert result.error is not None


def test_recommend_daily_returns_results():
    result = recommend("daily backup")
    assert result.has_results
    assert result.error is None


def test_recommend_hourly_contains_hourly_expression():
    result = recommend("run hourly")
    expressions = [r.expression for r in result.recommendations]
    assert any("@hourly" in e or "0 * * * *" in e for e in expressions)


def test_recommend_respects_top_n():
    result = recommend("daily morning weekly monthly", top_n=3)
    assert len(result.recommendations) <= 3


def test_recommend_no_match_returns_error_or_empty():
    result = recommend("xyzzy_completely_unknown_query_12345")
    # Either no results or an error message is acceptable
    assert result.error is not None or not result.has_results


def test_recommend_result_scores_between_zero_and_one():
    result = recommend("weekly cleanup")
    for rec in result.recommendations:
        assert 0.0 <= rec.score <= 1.0


def test_recommend_deduplicates_expressions():
    result = recommend("daily")
    expressions = [r.expression for r in result.recommendations]
    assert len(expressions) == len(set(expressions))


def test_recommend_each_result_has_explanation():
    result = recommend("morning daily")
    for rec in result.recommendations:
        assert rec.explanation  # non-empty string


def test_recommend_each_result_has_reason():
    result = recommend("midnight backup")
    for rec in result.recommendations:
        assert rec.reason


# ---------------------------------------------------------------------------
# format_recommendation()
# ---------------------------------------------------------------------------

def _make_rec() -> Recommendation:
    return Recommendation(
        expression="0 0 * * *",
        explanation="At midnight every day",
        reason="Matches keyword 'daily'",
        score=0.75,
    )


def test_format_recommendation_contains_expression():
    out = format_recommendation(_make_rec())
    assert "0 0 * * *" in out


def test_format_recommendation_contains_explanation():
    out = format_recommendation(_make_rec())
    assert "midnight" in out.lower() or "explanation" in out.lower()


def test_format_recommendation_with_index():
    out = format_recommendation(_make_rec(), index=2)
    assert "2." in out


def test_format_recommendation_without_index():
    out = format_recommendation(_make_rec(), index=None)
    assert "1." not in out


# ---------------------------------------------------------------------------
# format_result()
# ---------------------------------------------------------------------------

def test_format_result_shows_query():
    result = recommend("daily")
    out = format_result(result)
    assert "daily" in out


def test_format_result_error_shows_error_message():
    result = RecommendationResult(query="", error="Query must not be empty.")
    out = format_result(result)
    assert "empty" in out.lower() or "!" in out


def test_format_result_with_recommendations_shows_expressions():
    result = recommend("hourly")
    out = format_result(result)
    assert any(rec.expression in out for rec in result.recommendations)


# ---------------------------------------------------------------------------
# format_summary()
# ---------------------------------------------------------------------------

def test_format_summary_counts_queries():
    results = [recommend("daily"), recommend("hourly")]
    out = format_summary(results)
    assert "2" in out


def test_format_summary_counts_errors():
    results = [recommend(""), recommend("daily")]
    out = format_summary(results)
    assert "Error" in out or "error" in out
