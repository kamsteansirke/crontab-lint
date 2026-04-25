"""Tests for crontab_lint.expression_statistics."""

import pytest
from crontab_lint.expression_statistics import compute, ExpressionStatistics


def test_empty_input_returns_zero_totals():
    stats = compute([])
    assert stats.total == 0
    assert stats.valid == 0
    assert stats.invalid == 0


def test_blank_and_comment_lines_are_skipped():
    stats = compute(["", "   ", "# this is a comment"])
    assert stats.total == 0


def test_valid_expression_counted():
    stats = compute(["0 9 * * 1"])
    assert stats.total == 1
    assert stats.valid == 1
    assert stats.invalid == 0


def test_invalid_expression_counted():
    stats = compute(["not a cron"])
    assert stats.total == 1
    assert stats.valid == 0
    assert stats.invalid == 1


def test_invalid_expression_recorded():
    stats = compute(["bad expression"])
    assert "bad expression" in stats.invalid_expressions


def test_mixed_valid_and_invalid():
    lines = ["0 * * * *", "garbage", "30 6 * * *"]
    stats = compute(lines)
    assert stats.total == 3
    assert stats.valid == 2
    assert stats.invalid == 1


def test_valid_ratio_all_valid():
    stats = compute(["0 * * * *", "30 6 * * *"])
    assert stats.valid_ratio == pytest.approx(1.0)


def test_valid_ratio_all_invalid():
    stats = compute(["bad", "also bad"])
    assert stats.valid_ratio == pytest.approx(0.0)


def test_valid_ratio_empty():
    stats = compute([])
    assert stats.valid_ratio == pytest.approx(0.0)


def test_category_counts_populated():
    lines = ["* * * * *", "0 * * * *", "0 9 * * *"]
    stats = compute(lines)
    assert len(stats.category_counts) > 0


def test_most_common_category_set_when_valid_expressions_present():
    lines = ["0 9 * * *", "30 9 * * *", "* * * * *"]
    stats = compute(lines)
    assert stats.most_common_category != ""


def test_most_common_category_empty_when_no_valid():
    stats = compute(["bad"])
    assert stats.most_common_category == ""
