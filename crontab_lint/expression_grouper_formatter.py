"""Format grouped cron expressions for display."""

from __future__ import annotations

from typing import List

from .expression_grouper import ExpressionGroup, GroupingResult


def format_group(group: ExpressionGroup, show_index: bool = True) -> str:
    lines: List[str] = []
    header = f"[{group.label}]  ({group.size()} expression{'s' if group.size() != 1 else ''})"
    lines.append(header)
    for i, expr in enumerate(group.expressions, 1):
        prefix = f"  {i:>2}. " if show_index else "   - "
        lines.append(f"{prefix}{expr}")
    return "\n".join(lines)


def format_grouping(result: GroupingResult) -> str:
    lines: List[str] = []
    if not result.groups and not result.ungrouped:
        return "No expressions to group."

    for group in result.groups:
        lines.append(format_group(group))
        lines.append("")

    if result.ungrouped:
        lines.append("[Invalid / Ungrouped]")
        for expr in result.ungrouped:
            lines.append(f"   - {expr}")
        lines.append("")

    return "\n".join(lines).rstrip()


def format_summary(result: GroupingResult) -> str:
    total = sum(g.size() for g in result.groups)
    parts = [
        f"Groups: {result.group_count()}",
        f"Grouped: {total}",
        f"Ungrouped: {len(result.ungrouped)}",
    ]
    return "  ".join(parts)
