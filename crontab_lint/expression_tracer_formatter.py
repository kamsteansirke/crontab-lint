"""Format TraceResult objects for human-readable output."""
from __future__ import annotations

from typing import List

from .expression_tracer import TraceResult

_DATE_FMT = "%Y-%m-%d %H:%M"


def format_result(result: TraceResult) -> str:
    lines: List[str] = []
    lines.append(f"Expression : {result.expression}")

    if not result.is_valid:
        lines.append(f"Error      : {result.error}")
        return "\n".join(lines)

    lines.append(f"Triggers   : {result.count}")

    if not result.entries:
        lines.append("  (no triggers in the given window)")
        return "\n".join(lines)

    for entry in result.entries:
        ts = entry.trigger_time.strftime(_DATE_FMT)
        lines.append(f"  {entry.index:>4}. {ts}")

    return "\n".join(lines)


def format_results(results: List[TraceResult]) -> str:
    return "\n\n".join(format_result(r) for r in results)


def format_summary(results: List[TraceResult]) -> str:
    total_expr = len(results)
    valid = sum(1 for r in results if r.is_valid)
    total_triggers = sum(r.count for r in results if r.is_valid)
    lines = [
        f"Expressions traced : {total_expr}",
        f"Valid              : {valid}",
        f"Total triggers     : {total_triggers}",
    ]
    return "\n".join(lines)
