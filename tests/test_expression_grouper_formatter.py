"""Tests for crontab_lint.expression_grouper_formatter."""

from crontab_lint.expression_grouper import group, ExpressionGroup, GroupingResult
from crontab_lint.expression_grouper_formatter import (
    format_group,
    format_grouping,
    format_summary,
)


def _make_group(category: str, exprs) -> ExpressionGroup:
    return ExpressionGroup(
        label=category.title(), category=category, expressions=list(exprs)
    )


def test_format_group_contains_label():
    g = _make_group("daily", ["0 9 * * *"])
    output = format_group(g)
    assert "Daily" in output or "daily" in output.lower()


def test_format_group_contains_expression():
    g = _make_group("daily", ["0 9 * * *"])
    output = format_group(g)
    assert "0 9 * * *" in output


def test_format_group_shows_count():
    g = _make_group("hourly", ["0 * * * *", "30 * * * *"])
    output = format_group(g)
    assert "2" in output


def test_format_group_indexed():
    g = _make_group("daily", ["0 9 * * *"])
    output = format_group(g, show_index=True)
    assert "1." in output


def test_format_group_no_index():
    g = _make_group("daily", ["0 9 * * *"])
    output = format_group(g, show_index=False)
    assert "-" in output


def test_format_grouping_empty():
    result = GroupingResult(groups=[], ungrouped=[])
    output = format_grouping(result)
    assert "No expressions" in output


def test_format_grouping_shows_all_groups():
    result = group(["* * * * *", "0 9 * * *"])
    output = format_grouping(result)
    assert "* * * * *" in output
    assert "0 9 * * *" in output


def test_format_grouping_shows_ungrouped():
    result = group(["bad-expr"])
    output = format_grouping(result)
    assert "bad-expr" in output
    assert "Ungrouped" in output or "Invalid" in output


def test_format_summary_contains_group_count():
    result = group(["* * * * *"])
    summary = format_summary(result)
    assert "Groups:" in summary


def test_format_summary_contains_ungrouped_count():
    result = group(["bad"])
    summary = format_summary(result)
    assert "Ungrouped:" in summary
    assert "1" in summary
