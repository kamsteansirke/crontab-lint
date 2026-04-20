"""Tests for crontab_lint.annotator."""
import pytest
from crontab_lint.annotator import annotate_line, annotate, format_annotated


def test_blank_line():
    entry = annotate_line("")
    assert entry.is_blank
    assert entry.annotation is None
    assert entry.is_valid


def test_comment_line():
    entry = annotate_line("# this is a comment")
    assert entry.is_comment
    assert entry.annotation is None
    assert entry.is_valid


def test_valid_expression():
    entry = annotate_line("* * * * * echo hello")
    assert not entry.is_blank
    assert not entry.is_comment
    assert entry.is_valid
    assert entry.annotation is not None
    assert len(entry.annotation) > 0


def test_invalid_expression():
    entry = annotate_line("99 * * * *")
    assert not entry.is_valid
    assert entry.annotation is not None
    assert "ERROR" in entry.annotation


def test_annotate_list():
    lines = ["# header\n", "* * * * * job\n", "\n", "bad expression\n"]
    results = annotate(lines)
    assert len(results) == 4
    assert results[0].is_comment
    assert results[1].is_valid
    assert results[2].is_blank
    assert not results[3].is_valid


def test_format_annotated_valid():
    lines = ["0 9 * * 1 backup"]
    annotated = annotate(lines)
    output = format_annotated(annotated)
    assert "0 9 * * 1 backup" in output
    assert "#" in output


def test_format_annotated_blank_preserved():
    lines = ["", "* * * * * job"]
    annotated = annotate(lines)
    output = format_annotated(annotated)
    assert "\n" in output


def test_format_annotated_comment_char():
    lines = ["* * * * * task"]
    annotated = annotate(lines)
    output = format_annotated(annotated, comment_char="//")
    assert "//" in output


def test_format_annotated_error_line():
    lines = ["99 99 99 99 99"]
    annotated = annotate(lines)
    output = format_annotated(annotated)
    assert "ERROR" in output
