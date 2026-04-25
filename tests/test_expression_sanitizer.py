"""Tests for crontab_lint.expression_sanitizer."""

import pytest

from crontab_lint.expression_sanitizer import sanitize, sanitize_many, SanitizeResult


def test_clean_expression_is_unchanged():
    result = sanitize("0 9 * * 1")
    assert result.valid
    assert not result.changed
    assert result.sanitized == "0 9 * * 1"


def test_strips_leading_and_trailing_whitespace():
    result = sanitize("  0 9 * * 1  ")
    assert result.sanitized == "0 9 * * 1"
    assert result.changed


def test_collapses_internal_whitespace():
    result = sanitize("0  9   *  *  1")
    assert result.sanitized == "0 9 * * 1"
    assert result.changed


def test_strips_inline_comment():
    result = sanitize("0 9 * * 1 # run weekly")
    assert result.sanitized == "0 9 * * 1"
    assert result.changed
    assert result.valid


def test_strips_trailing_semicolon():
    result = sanitize("0 9 * * 1;")
    assert result.sanitized == "0 9 * * 1"
    assert result.changed
    assert result.valid


def test_special_string_is_valid():
    result = sanitize("@daily")
    assert result.valid
    assert result.sanitized == "@daily"


def test_invalid_expression_is_marked_invalid():
    result = sanitize("99 99 99 99 99")
    assert not result.valid
    assert result.error is not None
    assert len(result.error) > 0


def test_original_is_preserved():
    raw = "  0 9 * * 1  # weekly "
    result = sanitize(raw)
    assert result.original == raw


def test_changed_flag_false_when_no_change():
    result = sanitize("*/5 * * * *")
    assert not result.changed


def test_sanitize_many_returns_one_result_per_input():
    expressions = ["0 9 * * 1", "  @hourly  ", "bad expr"]
    results = sanitize_many(expressions)
    assert len(results) == 3


def test_sanitize_many_all_types():
    expressions = ["0 9 * * 1", "  @daily  ", "99 99 99 99 99"]
    results = sanitize_many(expressions)
    assert results[0].valid
    assert results[1].valid
    assert not results[2].valid


def test_sanitize_result_ok_matches_valid():
    valid_result = sanitize("0 0 * * *")
    invalid_result = sanitize("not valid at all")
    assert valid_result.ok() is True
    assert invalid_result.ok() is False


def test_combined_sanitization():
    result = sanitize("  0  9  *  *  1 # weekly job; ")
    assert result.sanitized == "0 9 * * 1"
    assert result.valid
    assert result.changed
