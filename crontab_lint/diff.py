"""Diff two sets of crontab expressions and report additions, removals, and changes."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from crontab_lint.parser import parse, ParseError
from crontab_lint.explainer import explain


@dataclass
class DiffEntry:
    expression: str
    status: str  # 'added' | 'removed' | 'changed'
    old_explanation: str | None = None
    new_explanation: str | None = None


@dataclass
class CronDiff:
    added: List[DiffEntry] = field(default_factory=list)
    removed: List[DiffEntry] = field(default_factory=list)
    changed: List[DiffEntry] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        return bool(self.added or self.removed or self.changed)


def _safe_explain(expr: str) -> str:
    try:
        return explain(parse(expr))
    except ParseError as exc:
        return f"(invalid: {exc})"


def diff(old_lines: List[str], new_lines: List[str]) -> CronDiff:
    """Compare two lists of crontab expression strings."""
    def _clean(lines: List[str]) -> dict[str, str]:
        result: dict[str, str] = {}
        for line in lines:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            result[stripped] = _safe_explain(stripped)
        return result

    old_map = _clean(old_lines)
    new_map = _clean(new_lines)

    old_keys = set(old_map)
    new_keys = set(new_map)

    result = CronDiff()

    for expr in sorted(new_keys - old_keys):
        result.added.append(DiffEntry(expr, "added", new_explanation=new_map[expr]))

    for expr in sorted(old_keys - new_keys):
        result.removed.append(DiffEntry(expr, "removed", old_explanation=old_map[expr]))

    for expr in sorted(old_keys & new_keys):
        if old_map[expr] != new_map[expr]:
            result.changed.append(
                DiffEntry(expr, "changed", old_explanation=old_map[expr], new_explanation=new_map[expr])
            )

    return result


def format_diff(cron_diff: CronDiff) -> str:
    lines: List[str] = []
    if not cron_diff.has_changes:
        return "No changes detected."
    for entry in cron_diff.added:
        lines.append(f"+ {entry.expression}")
        lines.append(f"  => {entry.new_explanation}")
    for entry in cron_diff.removed:
        lines.append(f"- {entry.expression}")
        lines.append(f"  => {entry.old_explanation}")
    for entry in cron_diff.changed:
        lines.append(f"~ {entry.expression}")
        lines.append(f"  old: {entry.old_explanation}")
        lines.append(f"  new: {entry.new_explanation}")
    return "\n".join(lines)
