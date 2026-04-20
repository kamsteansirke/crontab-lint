"""Formatting helpers for AuditLog entries."""

from __future__ import annotations

from typing import List

from .audit_log import AuditEntry

_ACTION_ICONS = {
    "lint": "🔍",
    "add": "➕",
    "remove": "➖",
    "edit": "✏️",
}


def format_entry(entry: AuditEntry, index: int | None = None) -> str:
    icon = _ACTION_ICONS.get(entry.action, "•")
    prefix = f"{index}. " if index is not None else ""
    actor_part = f" [{entry.actor}]" if entry.actor else ""
    detail_part = f" — {entry.detail}" if entry.detail else ""
    ts = entry.timestamp[:19].replace("T", " ")
    return (
        f"{prefix}{icon} {entry.action.upper()}{actor_part}  "
        f"{entry.expression}{detail_part}  ({ts})"
    )


def format_audit_log(entries: List[AuditEntry]) -> str:
    if not entries:
        return "No audit entries."
    lines = [format_entry(e, i + 1) for i, e in enumerate(entries)]
    return "\n".join(lines)


def format_summary(entries: List[AuditEntry]) -> str:
    counts: dict[str, int] = {}
    for e in entries:
        counts[e.action] = counts.get(e.action, 0) + 1
    if not counts:
        return "Audit log is empty."
    parts = ", ".join(f"{action}: {n}" for action, n in sorted(counts.items()))
    return f"Audit log — {len(entries)} entries ({parts})"
