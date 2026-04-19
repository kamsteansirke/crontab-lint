"""Export lint results to JSON or CSV formats."""
from __future__ import annotations
import csv
import io
import json
from typing import List

from crontab_lint.formatter import LintResult


def results_to_dict(result: LintResult) -> dict:
    return {
        "expression": result.expression,
        "valid": result.valid,
        "errors": result.errors,
        "explanation": result.explanation,
    }


def export_json(results: List[LintResult], indent: int = 2) -> str:
    """Serialize a list of LintResults to a JSON string."""
    return json.dumps([results_to_dict(r) for r in results], indent=indent)


def export_csv(results: List[LintResult]) -> str:
    """Serialize a list of LintResults to a CSV string."""
    output = io.StringIO()
    fieldnames = ["expression", "valid", "errors", "explanation"]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for result in results:
        d = results_to_dict(result)
        d["errors"] = "; ".join(d["errors"])
        writer.writerow(d)
    return output.getvalue()


def export(results: List[LintResult], fmt: str) -> str:
    """Export results in the given format ('json' or 'csv')."""
    if fmt == "json":
        return export_json(results)
    if fmt == "csv":
        return export_csv(results)
    raise ValueError(f"Unsupported export format: {fmt!r}")
