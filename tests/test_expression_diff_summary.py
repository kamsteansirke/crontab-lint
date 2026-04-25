"""Tests for expression_diff_summary and its formatter."""
import pytest

from crontab_lint.expression_diff_summary import (
    diff_expression_lists,
    DiffSummaryEntry,
    ExpressionDiffSummary,
)
from crontab_lint.expression_diff_summary_formatter import (
    format_entry,
    format_diff_summary,
    format_summary_stats,
)


# --- diff_expression_lists ---

def test_empty_lists_return_no_changes():
    result = diff_expression_lists([], [])
    assert not result.has_changes
    assert result.total_changes == 0


def test_added_expression_detected():
    result = diff_expression_lists([], ["0 9 * * 1"])
    assert len(result.added) == 1
    assert result.added[0].expression == "0 9 * * 1"
    assert result.added[0].status == "added"


def test_removed_expression_detected():
    result = diff_expression_lists(["0 9 * * 1"], [])
    assert len(result.removed) == 1
    assert result.removed[0].expression == "0 9 * * 1"
    assert result.removed[0].status == "removed"


def test_unchanged_expression_detected():
    result = diff_expression_lists(["0 9 * * 1"], ["0 9 * * 1"])
    assert len(result.unchanged) == 1
    assert result.unchanged[0].status == "unchanged"
    assert not result.has_changes


def test_changed_expression_appears_as_add_and_remove():
    result = diff_expression_lists(["0 9 * * 1"], ["0 10 * * 1"])
    assert len(result.added) == 1
    assert len(result.removed) == 1
    assert result.has_changes


def test_blank_and_comment_lines_skipped():
    result = diff_expression_lists(
        ["", "# comment", "0 9 * * 1"],
        ["", "# another comment", "0 9 * * 1"],
    )
    assert not result.has_changes


def test_explanation_populated_for_valid_expression():
    result = diff_expression_lists([], ["0 9 * * *"])
    entry = result.added[0]
    assert entry.explanation is not None
    assert len(entry.explanation) > 0


def test_explanation_none_for_invalid_expression():
    result = diff_expression_lists([], ["not-a-cron"])
    entry = result.added[0]
    assert entry.explanation is None


def test_all_entries_combines_all_lists():
    result = diff_expression_lists(["0 8 * * *"], ["0 9 * * *"])
    assert len(result.all_entries) == 2


# --- formatter ---

def test_format_entry_added_shows_plus():
    entry = DiffSummaryEntry("0 9 * * *", "added", "At 09:00")
    text = format_entry(entry)
    assert "[+]" in text
    assert "0 9 * * *" in text


def test_format_entry_removed_shows_minus():
    entry = DiffSummaryEntry("0 9 * * *", "removed", "At 09:00")
    text = format_entry(entry)
    assert "[-]" in text


def test_format_entry_includes_explanation_by_default():
    entry = DiffSummaryEntry("0 9 * * *", "added", "At 09:00")
    text = format_entry(entry, show_explanation=True)
    assert "At 09:00" in text


def test_format_entry_hides_explanation_when_disabled():
    entry = DiffSummaryEntry("0 9 * * *", "added", "At 09:00")
    text = format_entry(entry, show_explanation=False)
    assert "At 09:00" not in text


def test_format_diff_summary_no_changes_message():
    summary = ExpressionDiffSummary()
    text = format_diff_summary(summary)
    assert "No changes" in text


def test_format_diff_summary_shows_added_section():
    result = diff_expression_lists([], ["0 9 * * *"])
    text = format_diff_summary(result)
    assert "Added" in text


def test_format_diff_summary_shows_removed_section():
    result = diff_expression_lists(["0 9 * * *"], [])
    text = format_diff_summary(result)
    assert "Removed" in text


def test_format_diff_summary_unchanged_hidden_by_default():
    result = diff_expression_lists(["0 9 * * *"], ["0 9 * * *"])
    text = format_diff_summary(result)
    assert "Unchanged" not in text


def test_format_diff_summary_unchanged_shown_when_requested():
    result = diff_expression_lists(["0 9 * * *"], ["0 9 * * *"])
    text = format_diff_summary(result, show_unchanged=True)
    assert "Unchanged" in text


def test_format_summary_stats_shows_counts():
    result = diff_expression_lists(["0 8 * * *"], ["0 9 * * *"])
    text = format_summary_stats(result)
    assert "added=1" in text
    assert "removed=1" in text
    assert "changes detected" in text


def test_format_summary_stats_no_changes():
    result = diff_expression_lists(["0 9 * * *"], ["0 9 * * *"])
    text = format_summary_stats(result)
    assert "no changes" in text
