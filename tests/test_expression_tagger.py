"""Tests for expression_tagger."""
import pytest
from crontab_lint.expression_tagger import auto_tag, TaggingResult


def test_every_minute_is_valid():
    result = auto_tag("* * * * *")
    assert result.is_valid


def test_every_minute_has_every_minute_tag():
    result = auto_tag("* * * * *")
    assert result.has_tag("every_minute")


def test_specific_time_no_every_minute_tag():
    result = auto_tag("0 9 * * *")
    assert not result.has_tag("every_minute")


def test_step_expression_has_step_tag():
    result = auto_tag("*/15 * * * *")
    assert result.has_tag("step")


def test_range_expression_has_range_tag():
    result = auto_tag("0 9-17 * * *")
    assert result.has_tag("range")


def test_list_expression_has_list_tag():
    result = auto_tag("0 8,12,18 * * *")
    assert result.has_tag("list")


def test_special_string_daily():
    result = auto_tag("@daily")
    assert result.is_valid
    assert result.has_tag("daily")


def test_special_string_hourly():
    result = auto_tag("@hourly")
    assert result.has_tag("hourly")
    assert result.has_tag("frequent")


def test_special_string_yearly():
    result = auto_tag("@yearly")
    assert result.has_tag("yearly")
    assert result.has_tag("rare")


def test_special_string_reboot():
    result = auto_tag("@reboot")
    assert result.has_tag("reboot")
    assert result.has_tag("system")


def test_invalid_expression_is_not_valid():
    result = auto_tag("99 99 99 99 99")
    assert not result.is_valid
    assert result.error is not None


def test_invalid_expression_has_no_tags():
    result = auto_tag("not a cron")
    assert result.tags == []


def test_tags_are_deduplicated():
    result = auto_tag("* * * * *")
    assert len(result.tags) == len(set(result.tags))


def test_expression_stored_on_result():
    result = auto_tag("0 0 * * 0")
    assert result.expression == "0 0 * * 0"


def test_case_insensitive_special_string():
    result = auto_tag("@DAILY")
    assert result.is_valid
    assert result.has_tag("daily")
