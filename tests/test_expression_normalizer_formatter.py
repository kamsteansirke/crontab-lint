"""Tests for expression_normalizer_formatter module."""
import pytest
from crontab_lint.expression_normalizer import NormalizeResult
from crontab_lint.expression_normalizer_formatter import (
    format_result,
    format_results,
    format_summary,
)


def _changed(orig: str, norm: str) -> NormalizeResult:
    return NormalizeResult(original=orig, normalized=norm, changed=True)


def _unchanged(expr: str) -> NormalizeResult:
    return NormalizeResult(original=expr, normalized=expr, changed=False)


def _error(expr: str) -> NormalizeResult:
    return NormalizeResult(original=expr, normalized=None, changed=False, error="bad input")


def test_format_result_changed_shows_normalized():
    r = _changed("@daily", "0 0 * * *")
    out = format_result(r)
    assert "NORMALIZED" in out
    assert "@daily" in out
    assert "0 0 * * *" in out


def test_format_result_unchanged_shows_unchanged():
    r = _unchanged("0 9 * * 1")
    out = format_result(r)
    assert "UNCHANGED" in out
    assert "0 9 * * 1" in out


def test_format_result_error_shows_error():
    r = _error("garbage")
    out = format_result(r)
    assert "ERROR" in out
    assert "garbage" in out
    assert "bad input" in out


def test_format_result_with_index():
    r = _unchanged("* * * * *")
    out = format_result(r, index=3)
    assert out.startswith("3.")


def test_format_results_numbers_entries():
    results = [_unchanged("* * * * *"), _changed("@daily", "0 0 * * *")]
    out = format_results(results)
    assert "1." in out
    assert "2." in out


def test_format_results_empty():
    out = format_results([])
    assert "no expressions" in out


def test_format_summary_counts():
    results = [
        _changed("@daily", "0 0 * * *"),
        _unchanged("0 9 * * 1"),
        _error("bad"),
    ]
    out = format_summary(results)
    assert "Total: 3" in out
    assert "Normalized: 1" in out
    assert "Unchanged: 1" in out
    assert "Errors: 1" in out


def test_format_summary_all_unchanged():
    results = [_unchanged("* * * * *"), _unchanged("0 0 * * *")]
    out = format_summary(results)
    assert "Normalized: 0" in out
    assert "Errors: 0" in out
