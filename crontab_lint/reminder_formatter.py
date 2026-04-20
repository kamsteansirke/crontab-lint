"""Formatting helpers for Reminder objects."""
from __future__ import annotations

from typing import List

from .reminder import Reminder


def format_reminder(reminder: Reminder, index: int | None = None) -> str:
    prefix = f"{index}. " if index is not None else ""
    lines = [f"{prefix}[{reminder.expression}] {reminder.note}"]
    if reminder.due:
        overdue_flag = " (OVERDUE)" if reminder.is_overdue() else ""
        lines.append(f"   Due: {reminder.due}{overdue_flag}")
    if reminder.tags:
        lines.append(f"   Tags: {', '.join(reminder.tags)}")
    lines.append(f"   Created: {reminder.created_at}")
    return "\n".join(lines)


def format_reminders(reminders: List[Reminder]) -> str:
    if not reminders:
        return "No reminders found."
    return "\n\n".join(
        format_reminder(r, index=i + 1) for i, r in enumerate(reminders)
    )


def format_summary(reminders: List[Reminder]) -> str:
    total = len(reminders)
    overdue = sum(1 for r in reminders if r.is_overdue())
    parts = [f"Total reminders: {total}"]
    if overdue:
        parts.append(f"Overdue: {overdue}")
    return "  ".join(parts)
