"""Summarize multiple crontab expressions into a human-readable report."""

from dataclasses import dataclass, field
from typing import List

from .parser import CronExpression, parse, ParseError
from .explainer import explain
from .conflict_detector import detect_conflicts, ConflictReport


@dataclass
class Summary:
    total: int = 0
    valid: int = 0
    invalid: int = 0
    expressions: List[CronExpression] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    conflict_report: ConflictReport = None


def summarize(lines: List[str]) -> Summary:
    """Parse and summarize a list of crontab expression strings."""
    summary = Summary()
    parsed_expressions = []

    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        summary.total += 1
        try:
            expr = parse(line)
            parsed_expressions.append(expr)
            summary.expressions.append(expr)
            summary.valid += 1
        except ParseError as e:
            summary.invalid += 1
            summary.errors.append(f"{line!r}: {e}")

    summary.conflict_report = detect_conflicts(parsed_expressions)
    return summary


def format_summary(summary: Summary) -> str:
    """Format a Summary into a printable string."""
    lines = [
        f"Total expressions : {summary.total}",
        f"Valid             : {summary.valid}",
        f"Invalid           : {summary.invalid}",
    ]

    if summary.errors:
        lines.append("\nErrors:")
        for err in summary.errors:
            lines.append(f"  - {err}")

    if summary.expressions:
        lines.append("\nValid expressions:")
        for expr in summary.expressions:
            lines.append(f"  {expr.raw:<40} => {explain(expr)}")

    cr = summary.conflict_report
    if cr and cr.conflicts:
        lines.append(f"\nConflicts detected: {len(cr.conflicts)}")
        for c in cr.conflicts:
            lines.append(f"  - {c.description}")
    elif cr:
        lines.append("\nNo conflicts detected.")

    return "\n".join(lines)
