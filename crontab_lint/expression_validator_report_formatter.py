"""Formatter for ValidationReport objects."""
from __future__ import annotations

from typing import Optional

from .expression_validator_report import ValidationEntry, ValidationReport

_VALID_MARK = "✔"
_INVALID_MARK = "✘"


def format_entry(entry: ValidationEntry, index: Optional[int] = None) -> str:
    """Format a single ValidationEntry as a human-readable string."""
    prefix = f"{index}. " if index is not None else ""
    mark = _VALID_MARK if entry.valid else _INVALID_MARK
    lines = [f"{prefix}[{mark}] {entry.expression}"]
    if entry.valid and entry.explanation:
        lines.append(f"    Explanation : {entry.explanation}")
    if not entry.valid and entry.error:
        lines.append(f"    Error       : {entry.error}")
    return "\n".join(lines)


def format_report(report: ValidationReport) -> str:
    """Format a full ValidationReport."""
    if not report.entries:
        return "No expressions to validate."
    parts = []
    for idx, entry in enumerate(report.entries, start=1):
        parts.append(format_entry(entry, index=idx))
    return "\n".join(parts)


def format_summary(report: ValidationReport) -> str:
    """Return a one-line summary of the validation report."""
    return (
        f"Validated {report.total} expression(s): "
        f"{report.valid_count} valid, {report.invalid_count} invalid."
    )
