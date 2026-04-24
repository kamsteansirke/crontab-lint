"""Tests for expression_deduplicator module."""
import pytest

from crontab_lint.expression_deduplicator import (
    deduplicate,
    DeduplicationResult,
    DuplicateGroup,
)
from crontab_lint.expression_deduplicator_formatter import (
    format_group,
    format_result,
    format_summary,
)


def test_empty_input_returns_empty_result():
    result = deduplicate([])
    assert result.groups == []
    assert result.invalid == []
    assert not result.has_duplicates


def test_blank_and_comment_lines_are_skipped():
    result = deduplicate(["", "  ", "# daily backup", "0 0 * * *"])
    assert len(result.groups) == 1
    assert result.invalid == []


def test_invalid_expression_goes_to_invalid_list():
    result = deduplicate(["not-a-cron"])
    assert result.invalid == ["not-a-cron"]
    assert result.groups == []


def test_unique_expressions_produce_separate_groups():
    result = deduplicate(["0 0 * * *", "0 12 * * *"])
    assert len(result.groups) == 2
    assert not result.has_duplicates


def test_identical_expressions_are_grouped():
    result = deduplicate(["0 0 * * *", "0 0 * * *"])
    assert result.has_duplicates
    assert result.duplicate_count == 1
    assert len(result.duplicate_groups) == 1


def test_equivalent_special_string_and_expanded_are_grouped():
    # @daily normalises to 0 0 * * *
    result = deduplicate(["@daily", "0 0 * * *"])
    assert result.has_duplicates
    assert len(result.duplicate_groups) == 1


def test_duplicate_group_size():
    result = deduplicate(["* * * * *", "* * * * *", "* * * * *"])
    assert result.duplicate_count == 2
    assert result.unique_count == 1


def test_unique_count_reflects_distinct_canonicals():
    result = deduplicate(["0 0 * * *", "0 12 * * *", "@daily"])
    # @daily == 0 0 * * * so 2 unique canonicals
    assert result.unique_count == 2


def test_format_group_contains_canonical():
    group = DuplicateGroup(canonical="0 0 * * *", expressions=["@daily", "0 0 * * *"])
    output = format_group(group)
    assert "0 0 * * *" in output


def test_format_group_marks_duplicates():
    group = DuplicateGroup(canonical="0 0 * * *", expressions=["@daily", "0 0 * * *"])
    output = format_group(group)
    assert "DUPLICATE" in output


def test_format_group_unique_label():
    group = DuplicateGroup(canonical="0 12 * * *", expressions=["0 12 * * *"])
    output = format_group(group)
    assert "unique" in output


def test_format_result_no_duplicates_message():
    result = deduplicate(["0 0 * * *", "0 12 * * *"])
    output = format_result(result)
    assert "No duplicates" in output


def test_format_result_shows_duplicate_groups():
    result = deduplicate(["* * * * *", "* * * * *"])
    output = format_result(result)
    assert "Duplicate" in output


def test_format_summary_contains_counts():
    result = deduplicate(["0 0 * * *", "@daily", "0 12 * * *"])
    summary = format_summary(result)
    assert "Total" in summary
    assert "Unique" in summary
    assert "Duplicates" in summary
