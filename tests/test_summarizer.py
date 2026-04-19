"""Tests for crontab_lint.summarizer."""

import pytest
from crontab_lint.summarizer import summarize, format_summary


VALID_DAILY = "0 9 * * * /usr/bin/backup"
VALID_HOURLY = "0 * * * * /usr/bin/check"
INVALID_EXPR = "99 * * * *"  # invalid minute
COMMENT_LINE = "# this is a comment"
BLANK_LINE = ""


def test_summarize_empty():
    summary = summarize([])
    assert summary.total == 0
    assert summary.valid == 0
    assert summary.invalid == 0


def test_summarize_skips_comments_and_blanks():
    summary = summarize([COMMENT_LINE, BLANK_LINE, "  "])
    assert summary.total == 0


def test_summarize_valid_expressions():
    summary = summarize([VALID_DAILY, VALID_HOURLY])
    assert summary.total == 2
    assert summary.valid == 2
    assert summary.invalid == 0
    assert len(summary.expressions) == 2
    assert summary.errors == []


def test_summarize_invalid_expression():
    summary = summarize([INVALID_EXPR])
    assert summary.total == 1
    assert summary.valid == 0
    assert summary.invalid == 1
    assert len(summary.errors) == 1


def test_summarize_mixed():
    lines = [VALID_DAILY, INVALID_EXPR, COMMENT_LINE, VALID_HOURLY]
    summary = summarize(lines)
    assert summary.total == 3
    assert summary.valid == 2
    assert summary.invalid == 1


def test_summarize_has_conflict_report():
    summary = summarize([VALID_DAILY, VALID_HOURLY])
    assert summary.conflict_report is not None


def test_format_summary_contains_totals():
    summary = summarize([VALID_DAILY, VALID_HOURLY])
    output = format_summary(summary)
    assert "Total expressions" in output
    assert "Valid" in output
    assert "Invalid" in output


def test_format_summary_lists_errors():
    summary = summarize([INVALID_EXPR])
    output = format_summary(summary)
    assert "Errors" in output
    assert INVALID_EXPR in output


def test_format_summary_no_conflicts_message():
    summary = summarize([VALID_DAILY])
    output = format_summary(summary)
    assert "No conflicts detected" in output or "Conflicts detected" in output
