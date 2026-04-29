"""Tests for expression_mutation module."""

import pytest
from crontab_lint.expression_mutation import (
    MutationVariant,
    MutationResult,
    mutate,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _result(expression: str, count: int = 3) -> MutationResult:
    return mutate(expression, count=count)


# ---------------------------------------------------------------------------
# MutationResult basics
# ---------------------------------------------------------------------------

def test_mutate_returns_mutation_result():
    result = _result("0 9 * * 1")
    assert isinstance(result, MutationResult)


def test_mutate_invalid_expression_is_not_valid():
    result = _result("not a cron")
    assert not result.valid


def test_mutate_invalid_expression_has_error():
    result = _result("not a cron")
    assert result.error is not None
    assert len(result.error) > 0


def test_mutate_invalid_expression_has_no_variants():
    result = _result("not a cron")
    assert result.count == 0
    assert result.variants == []


def test_mutate_valid_expression_is_valid():
    result = _result("0 9 * * 1")
    assert result.valid


def test_mutate_valid_expression_has_no_error():
    result = _result("0 9 * * 1")
    assert result.error is None


# ---------------------------------------------------------------------------
# Variant count
# ---------------------------------------------------------------------------

def test_mutate_returns_up_to_count_variants():
    result = _result("0 9 * * 1", count=5)
    assert result.count <= 5


def test_mutate_count_zero_returns_no_variants():
    result = _result("0 9 * * 1", count=0)
    assert result.count == 0


def test_mutate_every_minute_produces_variants():
    result = _result("* * * * *", count=4)
    assert result.count > 0


def test_mutate_specific_time_produces_variants():
    result = _result("30 6 * * *", count=4)
    assert result.count > 0


# ---------------------------------------------------------------------------
# MutationVariant structure
# ---------------------------------------------------------------------------

def test_variant_has_expression():
    result = _result("0 9 * * 1", count=3)
    for variant in result.variants:
        assert isinstance(variant.expression, str)
        assert len(variant.expression) > 0


def test_variant_has_description():
    result = _result("0 9 * * 1", count=3)
    for variant in result.variants:
        assert isinstance(variant.description, str)
        assert len(variant.description) > 0


def test_variant_has_field_name():
    result = _result("0 9 * * 1", count=3)
    valid_fields = {"minute", "hour", "day_of_month", "month", "day_of_week"}
    for variant in result.variants:
        assert variant.field in valid_fields


def test_variant_expression_differs_from_original():
    result = _result("0 9 * * 1", count=5)
    for variant in result.variants:
        assert variant.expression != "0 9 * * 1"


def test_variant_expressions_are_unique():
    result = _result("0 9 * * 1", count=10)
    expressions = [v.expression for v in result.variants]
    assert len(expressions) == len(set(expressions))


# ---------------------------------------------------------------------------
# Original expression stored on result
# ---------------------------------------------------------------------------

def test_mutate_stores_original_expression():
    result = _result("0 9 * * 1")
    assert result.expression == "0 9 * * 1"


def test_mutate_invalid_stores_original_expression():
    result = _result("bad expr")
    assert result.expression == "bad expr"


# ---------------------------------------------------------------------------
# Special strings
# ---------------------------------------------------------------------------

def test_mutate_special_daily_is_valid():
    result = _result("@daily")
    assert result.valid


def test_mutate_special_hourly_produces_variants():
    result = _result("@hourly", count=3)
    assert result.count > 0
