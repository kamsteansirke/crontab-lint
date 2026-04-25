"""Formatter for ExpressionDiffSummary results."""
from __future__ import annotations

from typing import List

from crontab_lint.expression_diff_summary import DiffSummaryEntry, ExpressionDiffSummary

_ICONS = {
    "added": "+",
    "removed": "-",
    "unchanged": " ",
}


def format_entry(entry: DiffSummaryEntry, show_explanation: bool = True) -> str:
    icon = _ICONS.get(entry.status, "?")
    line = f"[{icon}] {entry.expression}"
    if show_explanation and entry.explanation:
        line += f"\n      {entry.explanation}"
    return line


def format_diff_summary(
    summary: ExpressionDiffSummary,
    show_unchanged: bool = False,
    show_explanation: bool = True,
) -> str:
    lines: List[str] = []

    if summary.added:
        lines.append("Added:")
        for entry in summary.added:
            lines.append(f"  {format_entry(entry, show_explanation)}")

    if summary.removed:
        lines.append("Removed:")
        for entry in summary.removed:
            lines.append(f"  {format_entry(entry, show_explanation)}")

    if show_unchanged and summary.unchanged:
        lines.append("Unchanged:")
        for entry in summary.unchanged:
            lines.append(f"  {format_entry(entry, show_explanation)}")

    if not lines:
        lines.append("No changes detected.")

    return "\n".join(lines)


def format_summary_stats(summary: ExpressionDiffSummary) -> str:
    parts = [
        f"added={len(summary.added)}",
        f"removed={len(summary.removed)}",
        f"unchanged={len(summary.unchanged)}",
    ]
    status = "changes detected" if summary.has_changes else "no changes"
    return f"Diff summary: {', '.join(parts)} ({status})"
