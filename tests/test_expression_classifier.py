"""Tests for expression_classifier and expression_classifier_formatter."""
import pytest

from crontab_lint.expression_classifier import (
    ClassificationResult,
    classify,
    classify_many,
)
from crontab_lint.expression_classifier_formatter import (
    format_result,
    format_results,
    format_summary,
)


# ---------------------------------------------------------------------------
# classify()
# ---------------------------------------------------------------------------

def test_classify_invalid_expression_is_not_valid():
    result = classify("not a cron")
    assert not result.is_valid


def test_classify_invalid_has_error_message():
    result = classify("not a cron")
    assert result.error


def test_classify_every_minute_is_valid():
    result = classify("* * * * *")
    assert result.is_valid


def test_classify_every_minute_category_is_real_time():
    result = classify("* * * * *")
    assert result.category == "real-time"


def test_classify_every_minute_subcategory():
    result = classify("* * * * *")
    assert result.subcategory == "every-minute"


def test_classify_every_minute_has_high_frequency_label():
    result = classify("* * * * *")
    assert "high-frequency" in result.labels


def test_classify_daily_midnight_is_scheduled():
    result = classify("0 0 * * *")
    assert result.category == "scheduled"
    assert result.subcategory == "once-daily"


def test_classify_daily_has_low_frequency_label():
    result = classify("0 0 * * *")
    assert "low-frequency" in result.labels


def test_classify_special_string_daily():
    result = classify("@daily")
    assert result.is_valid
    assert result.category == "scheduled"


def test_classify_special_string_hourly():
    result = classify("@hourly")
    assert result.is_valid
    assert result.category in ("frequent", "periodic", "scheduled")


def test_classify_returns_classification_result_instance():
    result = classify("0 12 * * 1")
    assert isinstance(result, ClassificationResult)


# ---------------------------------------------------------------------------
# classify_many()
# ---------------------------------------------------------------------------

def test_classify_many_skips_blank_lines():
    results = classify_many(["* * * * *", "", "0 0 * * *"])
    assert len(results) == 2


def test_classify_many_skips_comment_lines():
    results = classify_many(["# comment", "* * * * *"])
    assert len(results) == 1


def test_classify_many_returns_all_valid_for_clean_input():
    results = classify_many(["* * * * *", "0 0 * * *", "0 12 * * 1"])
    assert all(r.is_valid for r in results)


# ---------------------------------------------------------------------------
# Formatter tests
# ---------------------------------------------------------------------------

def test_format_result_valid_contains_expression():
    result = classify("* * * * *")
    text = format_result(result)
    assert "* * * * *" in text


def test_format_result_valid_contains_category():
    result = classify("* * * * *")
    text = format_result(result)
    assert "real-time" in text


def test_format_result_invalid_contains_error():
    result = classify("bad expr")
    text = format_result(result)
    assert "Error" in text


def test_format_result_with_index():
    result = classify("0 0 * * *")
    text = format_result(result, index=3)
    assert text.startswith("3.")


def test_format_results_empty_returns_message():
    text = format_results([])
    assert "No expressions" in text


def test_format_results_multiple_separated():
    results = classify_many(["* * * * *", "0 0 * * *"])
    text = format_results(results)
    assert "* * * * *" in text
    assert "0 0 * * *" in text


def test_format_summary_shows_total():
    results = classify_many(["* * * * *", "0 0 * * *"])
    text = format_summary(results)
    assert "Total: 2" in text


def test_format_summary_shows_valid_count():
    results = classify_many(["* * * * *", "bad"])
    text = format_summary(results)
    assert "Valid: 1" in text
    assert "Invalid: 1" in text
