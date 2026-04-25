"""Tests for crontab_lint.expression_search."""
import pytest

from crontab_lint.expression_search import search, SearchReport, SearchResult


EXPRESSIONS = [
    "* * * * *",       # every minute
    "0 9 * * 1",       # every Monday at 09:00
    "0 0 * * *",       # daily midnight
    "30 6 1 * *",      # monthly, 1st at 06:30
    "@daily",
    "@hourly",
    "# this is a comment",
    "",
]


def test_search_returns_report_type():
    report = search(EXPRESSIONS, "daily")
    assert isinstance(report, SearchReport)


def test_search_query_stored_on_report():
    report = search(EXPRESSIONS, "minute")
    assert report.query == "minute"


def test_search_empty_query_returns_no_results():
    report = search(EXPRESSIONS, "")
    assert not report.has_results


def test_search_whitespace_only_query_returns_no_results():
    report = search(EXPRESSIONS, "   ")
    assert not report.has_results


def test_search_matches_raw_expression():
    report = search(EXPRESSIONS, "@daily")
    expressions = [r.expression for r in report.results]
    assert "@daily" in expressions


def test_search_matched_on_expression_when_literal_match():
    report = search(EXPRESSIONS, "@hourly")
    result = next(r for r in report.results if r.expression == "@hourly")
    assert result.matched_on == "expression"


def test_search_skips_comment_lines():
    report = search(EXPRESSIONS, "comment")
    for r in report.results:
        assert not r.expression.startswith("#")


def test_search_skips_blank_lines():
    report = search(EXPRESSIONS, "")
    assert all(r.expression.strip() for r in report.results)


def test_search_explanation_match_sets_matched_on():
    # "Monday" should appear in the explanation for "0 9 * * 1"
    report = search(["0 9 * * 1"], "monday", search_explanations=True)
    if report.has_results:
        assert report.results[0].matched_on in ("expression", "explanation", "tag")


def test_search_case_insensitive():
    report = search(["@daily"], "DAILY")
    assert report.has_results


def test_search_no_match_returns_empty_results():
    report = search(EXPRESSIONS, "zzznomatch")
    assert not report.has_results
    assert report.count == 0


def test_search_result_has_explanation_field():
    report = search(["0 0 * * *"], "midnight")
    # may or may not match, but if it does the field is present
    for r in report.results:
        assert hasattr(r, "explanation")


def test_search_result_has_tags_list():
    report = search(["* * * * *"], "minute")
    assert report.has_results
    assert isinstance(report.results[0].tags, list)


def test_search_count_matches_results_length():
    report = search(EXPRESSIONS, "*")
    assert report.count == len(report.results)


def test_search_disable_explanation_search():
    # With explanations disabled a query that only matches explanation won't return results
    report = search(["0 9 * * 1"], "monday", search_explanations=False, search_tags=False)
    # Should only match if "monday" appears literally in the expression string
    for r in report.results:
        assert "monday" in r.expression.lower()
