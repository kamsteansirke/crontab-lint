"""Tests for crontab_lint.cli_export."""
import json
import csv
import io
import textwrap
from pathlib import Path

import pytest

from crontab_lint.cli_export import run_export


def test_no_args_returns_zero():
    assert run_export([]) == 0


def test_valid_expression_json(capsys):
    rc = run_export(["* * * * *"])
    assert rc == 0
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data[0]["valid"] is True


def test_invalid_expression_json(capsys):
    rc = run_export(["bad expr"])
    assert rc == 0
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data[0]["valid"] is False


def test_csv_format(capsys):
    rc = run_export(["--format", "csv", "0 12 * * *"])
    assert rc == 0
    out = capsys.readouterr().out
    rows = list(csv.DictReader(io.StringIO(out)))
    assert rows[0]["valid"] == "True"


def test_multiple_expressions_json(capsys):
    run_export(["* * * * *", "0 0 * * 0"])
    out = capsys.readouterr().out
    data = json.loads(out)
    assert len(data) == 2


def test_file_input_json(tmp_path, capsys):
    f = tmp_path / "crons.txt"
    f.write_text(textwrap.dedent("""\
        # daily
        0 0 * * *
        30 6 * * 1
    """))
    rc = run_export(["--file", str(f)])
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert len(data) == 2


def test_file_not_found_returns_one(capsys):
    rc = run_export(["--file", "/nonexistent/path.txt"])
    assert rc == 1
