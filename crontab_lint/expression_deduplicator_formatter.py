"""Format deduplication results for CLI output."""
from __future__ import annotations

from typing import List

from .expression_deduplicator import DeduplicationResult, DuplicateGroup


def format_group(group: DuplicateGroup, index: int | None = None) -> str:
    prefix = f"[{index}] " if index is not None else ""
    lines: List[str] = []
    status = "DUPLICATE" if group.is_duplicate else "unique"
    lines.append(f"{prefix}Canonical: {group.canonical}  [{status}]")
    for expr in group.expressions:
        marker = "  *" if group.is_duplicate else "   "
        lines.append(f"{marker} {expr}")
    return "\n".join(lines)


def format_result(result: DeduplicationResult) -> str:
    lines: List[str] = []

    if result.invalid:
        lines.append("Invalid expressions (skipped):")
        for expr in result.invalid:
            lines.append(f"  ! {expr}")
        lines.append("")

    if not result.groups:
        lines.append("No valid expressions to deduplicate.")
        return "\n".join(lines)

    if result.has_duplicates:
        lines.append("Duplicate groups found:")
        for i, group in enumerate(result.duplicate_groups, 1):
            lines.append(format_group(group, index=i))
            lines.append("")
    else:
        lines.append("No duplicates found.")

    return "\n".join(lines).rstrip()


def format_summary(result: DeduplicationResult) -> str:
    total = sum(g.size for g in result.groups)
    unique = result.unique_count
    dupes = result.duplicate_count
    invalid = len(result.invalid)
    parts = [
        f"Total: {total}",
        f"Unique: {unique}",
        f"Duplicates: {dupes}",
        f"Invalid: {invalid}",
    ]
    return "  ".join(parts)
