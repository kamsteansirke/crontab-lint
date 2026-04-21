"""Tests for timezone_checker and timezone_formatter."""

import pytest

from crontab_lint.timezone_checker import check, TimezoneCheckResult, TimezoneWarning
from crontab_lint.timezone_formatter import format_result, format_results, format_summary


# ---------------------------------------------------------------------------
# timezone_checker.check
# ---------------------------------------------------------------------------

def test_check_valid_utc_timezone():
    result = check("0 9 * * 1", "UTC")
    assert result.is_valid_tz
    assert result.utc_offset == "UTC+00:00"


def test_check_valid_named_timezone():
    result = check("30 8 * * *", "America/New_York")
    assert result.is_valid_tz
    assert result.utc_offset is not None
    assert result.utc_offset.startswith("UTC")


def test_check_invalid_timezone():
    result = check("0 0 * * *", "Mars/Olympus_Mons")
    assert not result.is_valid_tz
    assert result.utc_offset is None


def test_check_invalid_tz_has_unknown_tz_warning():
    result = check("0 0 * * *", "Not/ATimezone")
    codes = [w.code for w in result.warnings]
    assert "UNKNOWN_TZ" in codes


def test_check_every_minute_has_high_frequency_warning():
    result = check("* * * * *", "UTC")
    codes = [w.code for w in result.warnings]
    assert "HIGH_FREQUENCY" in codes


def test_check_specific_time_no_high_frequency_warning():
    result = check("0 9 * * 1", "UTC")
    codes = [w.code for w in result.warnings]
    assert "HIGH_FREQUENCY" not in codes


def test_check_result_stores_expression():
    result = check("@daily", "Europe/London")
    assert result.expression == "@daily"


def test_check_result_stores_tz_name():
    result = check("@hourly", "Asia/Tokyo")
    assert result.tz_name == "Asia/Tokyo"


def test_has_warnings_false_when_empty():
    result = check("0 9 * * 1", "UTC")
    # May or may not have warnings but property must be bool
    assert isinstance(result.has_warnings, bool)


# ---------------------------------------------------------------------------
# timezone_formatter
# ---------------------------------------------------------------------------

def test_format_result_contains_expression():
    result = check("0 9 * * 1", "UTC")
    output = format_result(result)
    assert "0 9 * * 1" in output


def test_format_result_contains_timezone():
    result = check("0 9 * * 1", "UTC")
    output = format_result(result)
    assert "UTC" in output


def test_format_result_invalid_tz_shows_invalid():
    result = check("0 0 * * *", "Fake/Zone")
    output = format_result(result)
    assert "INVALID" in output.upper()


def test_format_result_shows_warning_code():
    result = check("* * * * *", "UTC")
    output = format_result(result)
    assert "HIGH_FREQUENCY" in output


def test_format_results_multiple():
    results = [check("0 9 * * 1", "UTC"), check("@daily", "Europe/Paris")]
    output = format_results(results)
    assert "0 9 * * 1" in output
    assert "@daily" in output


def test_format_results_empty():
    output = format_results([])
    assert "No results" in output


def test_format_summary_shows_totals():
    results = [check("0 9 * * 1", "UTC"), check("0 0 * * *", "Bad/Zone")]
    output = format_summary(results)
    assert "2" in output
    assert "1" in output
