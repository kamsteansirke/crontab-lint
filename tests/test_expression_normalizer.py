"""Tests for expression_normalizer module."""
import pytest
from crontab_lint.expression_normalizer import normalize, NormalizeResult


def test_normalize_special_daily():
    result = normalize("@daily")
    assert result.ok
    assert result.normalized == "0 0 * * *"
    assert result.changed is True


def test_normalize_special_hourly():
    result = normalize("@hourly")
    assert result.ok
    assert result.normalized == "0 * * * *"
    assert result.changed is True


def test_normalize_special_yearly():
    result = normalize("@yearly")
    assert result.ok
    assert result.normalized == "0 0 1 1 *"


def test_normalize_annually_same_as_yearly():
    assert normalize("@annually").normalized == normalize("@yearly").normalized


def test_normalize_step_one_becomes_wildcard():
    result = normalize("*/1 * * * *")
    assert result.ok
    assert result.normalized == "* * * * *"
    assert result.changed is True


def test_normalize_already_canonical():
    result = normalize("0 9 * * 1")
    assert result.ok
    assert result.changed is False
    assert result.normalized == "0 9 * * 1"


def test_normalize_dow_name():
    result = normalize("0 9 * * mon")
    assert result.ok
    assert result.normalized == "0 9 * * 1"
    assert result.changed is True


def test_normalize_month_name():
    result = normalize("0 0 1 jan *")
    assert result.ok
    assert result.normalized == "0 0 1 1 *"


def test_normalize_invalid_expression_returns_error():
    result = normalize("not a cron")
    assert not result.ok
    assert result.error is not None
    assert result.normalized is None
    assert result.changed is False


def test_normalize_with_command():
    result = normalize("*/1 * * * * /usr/bin/backup")
    assert result.ok
    assert "*" in result.normalized
    assert "/usr/bin/backup" in result.normalized


def test_normalize_case_insensitive_special():
    result = normalize("@DAILY")
    assert result.ok
    assert result.normalized == "0 0 * * *"


def test_normalize_result_ok_property_true():
    r = NormalizeResult(original="* * * * *", normalized="* * * * *", changed=False)
    assert r.ok is True


def test_normalize_result_ok_property_false():
    r = NormalizeResult(original="bad", normalized=None, changed=False, error="oops")
    assert r.ok is False
