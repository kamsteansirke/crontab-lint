"""Format history entries for display."""
from __future__ import annotations

from typing import List

from crontab_lint.history import HistoryEntry


def format_entry(entry: HistoryEntry, index: int | None = None) -> str:
    prefix = f"{index:3}. " if index is not None else "    "
    status = "\u2713 VALID" if entry.valid else "\u2717 INVALID"
    line = f"{prefix}[{entry.timestamp}] {status:10} {entry.expression}"
    if entry.explanation:
        line += f"\n       Explanation: {entry.explanation}"
    return line


def format_history(entries: List[HistoryEntry]) -> str:
    if not entries:
        return "No history entries."
    lines = [format_entry(e, i) for i, e in enumerate(entries, 1)]
    return "\n".join(lines)


def format_summary(entries: List[HistoryEntry]) -> str:
    total = len(entries)
    valid = sum(1 for e in entries if e.valid)
    invalid = total - valid
    return (
        f"History: {total} total, {valid} valid, {invalid} invalid."
    )
