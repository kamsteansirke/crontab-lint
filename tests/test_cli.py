"""Tests for the CLI module."""
import pytest
from unittest.mock import patch, mock_open

from crontab_lint.cli import lint_expression, run


def test_lint_expression_valid():
    result = lint_expression("* * * * *")
    assert result.valid is True
    assert result.errors == []
    assert result.explanation is not None


def test_lint_expression_invalid():
    result = lint_expression("invalid expression here")
    assert result.valid is False
    assert len(result.errors) > 0


def test_lint_expression_special_string():
    result = lint_expression("@daily")
    assert result.valid is True


def test_run_no_args_returns_zero():
    exit_code = run([])
    assert exit_code == 0


def test_run_valid_expression_returns_zero(capsys):
    exit_code = run(["* * * * *"])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "* * * * *" in captured.out


def test_run_invalid_expression_returns_one(capsys):
    exit_code = run(["not a cron"])
    assert exit_code == 1
    captured = capsys.readouterr()
    assert "INVALID" in captured.out or "invalid" in captured.out.lower()


def test_run_multiple_expressions(capsys):
    exit_code = run(["* * * * *", "0 12 * * *"])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "* * * * *" in captured.out
    assert "0 12 * * *" in captured.out


def test_run_from_file(capsys, tmp_path):
    cron_file = tmp_path / "crontab.txt"
    cron_file.write_text("* * * * *\n# comment\n0 6 * * 1\n")
    exit_code = run(["--file", str(cron_file)])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "* * * * *" in captured.out
    assert "0 6 * * 1" in captured.out


def test_run_file_not_found():
    exit_code = run(["--file", "/nonexistent/path/crontab.txt"])
    assert exit_code == 2


def test_run_with_conflicts_flag(capsys):
    exit_code = run(["--conflicts", "* * * * *", "0 * * * *"])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "conflict" in captured.out.lower() or "No conflicts" in captured.out
