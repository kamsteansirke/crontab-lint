"""Tests for crontab_lint.diff."""
import pytest
from crontab_lint.diff import diff, format_diff


OLD = ["* * * * *", "0 9 * * 1", "30 6 * * *"]
NEW = ["* * * * *", "0 10 * * 1", "0 0 * * 0"]


def test_diff_added():
    result = diff(OLD, NEW)
    exprs = [e.expression for e in result.added]
    assert "0 0 * * 0" in exprs


def test_diff_removed():
    result = diff(OLD, NEW)
    exprs = [e.expression for e in result.removed]
    assert "30 6 * * *" in exprs


def test_diff_changed():
    result = diff(OLD, NEW)
    exprs = [e.expression for e in result.changed]
    assert "0 10 * * 1" in exprs or "0 9 * * 1" in exprs


def test_diff_unchanged_not_in_any_list():
    result = diff(OLD, NEW)
    all_exprs = (
        [e.expression for e in result.added]
        + [e.expression for e in result.removed]
        + [e.expression for e in result.changed]
    )
    assert "* * * * *" not in all_exprs


def test_diff_no_changes():
    result = diff(OLD, OLD)
    assert not result.has_changes


def test_diff_skips_comments():
    result = diff(["# comment", "* * * * *"], ["* * * * *"])
    assert not result.has_changes


def test_diff_skips_blank_lines():
    result = diff(["", "  ", "* * * * *"], ["* * * * *"])
    assert not result.has_changes


def test_format_diff_no_changes():
    result = diff(OLD, OLD)
    assert format_diff(result) == "No changes detected."


def test_format_diff_added_prefix():
    result = diff([], ["* * * * *"])
    output = format_diff(result)
    assert output.startswith("+")


def test_format_diff_removed_prefix():
    result = diff(["* * * * *"], [])
    output = format_diff(result)
    assert output.startswith("-")


def test_format_diff_contains_expression():
    result = diff(OLD, NEW)
    output = format_diff(result)
    assert "0 0 * * 0" in output
    assert "30 6 * * *" in output


def test_diff_entry_has_explanation():
    result = diff([], ["0 9 * * 1"])
    assert result.added[0].new_explanation is not None
    assert len(result.added[0].new_explanation) > 0
