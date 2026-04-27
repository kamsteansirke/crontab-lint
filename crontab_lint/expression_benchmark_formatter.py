"""Formatters for BenchmarkReport output."""
from __future__ import annotations

from typing import List

from .expression_benchmark import BenchmarkEntry, BenchmarkReport

_COST_SYMBOLS = {
    "very_high": "!!!!!",
    "high": "!!!!",
    "medium": "!!!",
    "low": "!!",
    "very_low": "!",
    "unknown": "?",
}


def format_entry(entry: BenchmarkEntry, index: int | None = None) -> str:
    prefix = f"{index}. " if index is not None else ""
    if not entry.is_valid:
        return f"{prefix}[INVALID] {entry.expression}  ({entry.error})"
    cost_sym = _COST_SYMBOLS.get(entry.cost_level, "?")
    rank_str = f"  rank=#{entry.rank}" if entry.rank else ""
    return (
        f"{prefix}{entry.expression}\n"
        f"  runs/day={entry.runs_per_day:.1f}  "
        f"category={entry.frequency_category}  "
        f"cost={entry.cost_level} {cost_sym}"
        f"{rank_str}"
    )


def format_report(report: BenchmarkReport) -> str:
    if not report.entries:
        return "No expressions to benchmark."
    lines: List[str] = ["Benchmark Report", "=" * 40]
    for i, entry in enumerate(report.entries, start=1):
        lines.append(format_entry(entry, index=i))
        lines.append("")
    return "\n".join(lines).rstrip()


def format_summary(report: BenchmarkReport) -> str:
    lines = [
        f"Total      : {report.total}",
        f"Valid      : {report.valid_count}",
        f"Invalid    : {report.invalid_count}",
    ]
    if report.valid_count:
        top = next(
            (e for e in report.entries if e.is_valid and e.rank == 1), None
        )
        if top:
            lines.append(f"Most freq. : {top.expression} ({top.runs_per_day:.1f}/day)")
    return "\n".join(lines)
