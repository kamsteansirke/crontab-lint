"""Tests for crontab_lint.expression_merger."""
import pytest
from crontab_lint.expression_merger import merge, MergeResult, MergeEntry


def test_merge_empty_input_returns_empty_result():
    result = merge([])
    assert isinstance(result, MergeResult)
    assert result.total == 0


def test_merge_skips_blank_lines():
    result = merge(["", "   ", "\t"])
    assert result.total == 0
    assert len(result.skipped) == 3


def test_merge_skips_comment_lines():
    result = merge(["# every minute", "#daily"])
    assert result.total == 0
    assert len(result.skipped) == 2


def test_merge_skips_invalid_expressions():
    result = merge(["not a cron"])
    assert result.total == 0
    assert "not a cron" in result.skipped


def test_merge_single_expression_returned_as_is():
    result = merge(["0 6 * * *"])
    assert result.total == 1
    entry = result.entries[0]
    assert entry.merged == "0 6 * * *"
    assert entry.is_valid


def test_merge_entry_has_explanation():
    result = merge(["0 6 * * *"])
    entry = result.entries[0]
    assert entry.explanation is not None
    assert len(entry.explanation) > 0


def test_merge_two_expressions_differing_in_hour():
    result = merge(["0 6 * * *", "0 7 * * *"])
    assert result.total == 1
    entry = result.entries[0]
    assert entry.is_valid
    assert "6,7" in entry.merged
    assert set(entry.original) == {"0 6 * * *", "0 7 * * *"}


def test_merge_two_expressions_differing_in_minute():
    result = merge(["0 6 * * *", "30 6 * * *"])
    assert result.total == 1
    entry = result.entries[0]
    assert "0,30" in entry.merged


def test_merge_non_mergeable_expressions_stay_separate():
    # differ in two fields — cannot be merged
    result = merge(["0 6 * * 1", "30 8 * * 2"])
    assert result.total == 2


def test_merge_three_expressions_two_mergeable_one_not():
    result = merge(["0 6 * * *", "0 7 * * *", "15 3 1 * *"])
    # first two merge; third stays alone
    assert result.total == 2


def test_merge_valid_count():
    result = merge(["0 6 * * *", "0 7 * * *", "15 3 1 * *"])
    assert result.valid_count == result.total


def test_merge_identical_expressions_not_merged():
    # identical expressions differ in zero fields — no merge
    result = merge(["0 6 * * *", "0 6 * * *"])
    assert result.total == 2


def test_merge_preserves_skipped_count_alongside_valid():
    result = merge(["# comment", "0 6 * * *", ""])
    assert result.total == 1
    assert len(result.skipped) == 2
