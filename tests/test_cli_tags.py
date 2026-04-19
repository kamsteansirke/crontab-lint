"""Tests for cli_tags module."""
import json
import pytest
from pathlib import Path
from crontab_lint.cli_tags import run_tags


def test_no_command_returns_zero():
    assert run_tags([]) == 0


def test_add_creates_file(tmp_path):
    reg_file = str(tmp_path / "tags.json")
    result = run_tags(["--file", reg_file, "add", "* * * * *", "--tags", "frequent"])
    assert result == 0
    assert Path(reg_file).exists()
    data = json.loads(Path(reg_file).read_text())
    assert len(data) == 1
    assert data[0]["expression"] == "* * * * *"
    assert "frequent" in data[0]["tags"]


def test_add_with_description(tmp_path):
    reg_file = str(tmp_path / "tags.json")
    run_tags(["--file", reg_file, "add", "0 0 * * *", "--tags", "daily", "--description", "Midnight job"])
    data = json.loads(Path(reg_file).read_text())
    assert data[0]["description"] == "Midnight job"


def test_find_existing_tag(tmp_path, capsys):
    reg_file = str(tmp_path / "tags.json")
    run_tags(["--file", reg_file, "add", "0 * * * *", "--tags", "hourly"])
    run_tags(["--file", reg_file, "find", "hourly"])
    captured = capsys.readouterr()
    assert "0 * * * *" in captured.out


def test_find_missing_tag(tmp_path, capsys):
    reg_file = str(tmp_path / "tags.json")
    run_tags(["--file", reg_file, "find", "ghost"])
    captured = capsys.readouterr()
    assert "No expressions found" in captured.out


def test_list_tags(tmp_path, capsys):
    reg_file = str(tmp_path / "tags.json")
    run_tags(["--file", reg_file, "add", "* * * * *", "--tags", "alpha", "beta"])
    run_tags(["--file", reg_file, "list-tags"])
    captured = capsys.readouterr()
    assert "alpha" in captured.out
    assert "beta" in captured.out


def test_list_tags_empty(tmp_path, capsys):
    reg_file = str(tmp_path / "tags.json")
    run_tags(["--file", reg_file, "list-tags"])
    captured = capsys.readouterr()
    assert "No tags" in captured.out


def test_remove_expression(tmp_path, capsys):
    reg_file = str(tmp_path / "tags.json")
    run_tags(["--file", reg_file, "add", "* * * * *", "--tags", "x"])
    run_tags(["--file", reg_file, "remove", "* * * * *"])
    data = json.loads(Path(reg_file).read_text())
    assert data == []
