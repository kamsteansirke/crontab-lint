"""Tests for crontab_lint.exporter."""
import csv
import io
import json
import pytest

from crontab_lint.formatter import LintResult
from crontab_lint.exporter import export_json, export_csv, export


def _valid(expr="* * * * *", explanation="Every minute"):
    return LintResult(expression=expr, valid=True, errors=[], explanation=explanation)


def _invalid(expr="bad", errors=None):
    return LintResult(expression=expr, valid=False, errors=errors or ["Too few fields"], explanation="")


def test_export_json_valid():
    out = export_json([_valid()])
    data = json.loads(out)
    assert len(data) == 1
    assert data[0]["valid"] is True
    assert data[0]["expression"] == "* * * * *"


def test_export_json_invalid():
    out = export_json([_invalid()])
    data = json.loads(out)
    assert data[0]["valid"] is False
    assert "Too few fields" in data[0]["errors"]


def test_export_json_multiple():
    out = export_json([_valid(), _invalid()])
    data = json.loads(out)
    assert len(data) == 2


def test_export_csv_headers():
    out = export_csv([_valid()])
    reader = csv.DictReader(io.StringIO(out))
    assert set(reader.fieldnames) == {"expression", "valid", "errors", "explanation"}


def test_export_csv_valid_row():
    out = export_csv([_valid()])
    rows = list(csv.DictReader(io.StringIO(out)))
    assert rows[0]["valid"] == "True"
    assert rows[0]["errors"] == ""


def test_export_csv_invalid_row():
    out = export_csv([_invalid()])
    rows = list(csv.DictReader(io.StringIO(out)))
    assert rows[0]["valid"] == "False"
    assert "Too few fields" in rows[0]["errors"]


def test_export_dispatch_json():
    out = export([_valid()], "json")
    json.loads(out)  # should not raise


def test_export_dispatch_csv():
    out = export([_valid()], "csv")
    assert "expression" in out


def test_export_unknown_format():
    with pytest.raises(ValueError, match="Unsupported"):
        export([_valid()], "xml")
