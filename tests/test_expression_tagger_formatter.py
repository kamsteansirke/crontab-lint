"""Tests for expression_tagger_formatter."""
import pytest
from crontab_lint.expression_tagger import auto_tag, TaggingResult
from crontab_lint.expression_tagger_formatter import (
    format_result,
    format_results,
    format_summary,
)


def _valid() -> TaggingResult:
    return auto_tag("0 9 * * *")


def _invalid() -> TaggingResult:
    return auto_tag("not a cron")


def test_format_result_contains_expression():
    r = _valid()
    assert r.expression in format_result(r)


def test_format_result_shows_tags():
    r = _valid()
    out = format_result(r)
    assert "tags:" in out


def test_format_result_invalid_shows_invalid():
    r = _invalid()
    out = format_result(r)
    assert "INVALID" in out


def test_format_result_invalid_shows_error():
    r = _invalid()
    out = format_result(r)
    assert r.error is not None
    assert r.error in out


def test_format_result_with_index():
    r = _valid()
    out = format_result(r, index=3)
    assert out.startswith("3.")


def test_format_result_no_index_no_prefix():
    r = _valid()
    out = format_result(r)
    assert not out.startswith("1.")


def test_format_results_empty():
    out = format_results([])
    assert "No expressions" in out


def test_format_results_numbered():
    results = [_valid(), _valid()]
    out = format_results(results, numbered=True)
    assert "1." in out
    assert "2." in out


def test_format_results_contains_all_expressions():
    r1 = auto_tag("0 9 * * *")
    r2 = auto_tag("@daily")
    out = format_results([r1, r2])
    assert r1.expression in out
    assert r2.expression in out


def test_format_summary_shows_totals():
    results = [_valid(), _valid(), _invalid()]
    out = format_summary(results)
    assert "Total: 3" in out
    assert "Valid: 2" in out
    assert "Invalid: 1" in out


def test_format_summary_shows_unique_tags():
    results = [auto_tag("@daily"), auto_tag("@hourly")]
    out = format_summary(results)
    assert "Unique tags:" in out
    assert "daily" in out
    assert "hourly" in out


def test_format_summary_no_tags_shows_none():
    results = [_invalid()]
    out = format_summary(results)
    assert "(none)" in out
