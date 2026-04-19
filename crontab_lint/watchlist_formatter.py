"""Formatting helpers for watchlist entries."""
from __future__ import annotations
from typing import List
from crontab_lint.watchlist import WatchedExpression, Watchlist


def format_entry(entry: WatchedExpression, index: Optional[int] = None) -> str:
    from typing import Optional
    prefix = f"{index}. " if index is not None else ""
    tags = f"  tags: {', '.join(entry.tags)}" if entry.tags else ""
    notes = f"  notes: {entry.notes}" if entry.notes else ""
    lines = [f"{prefix}[{entry.label}] {entry.expression}"]
    if tags:
        lines.append(tags)
    if notes:
        lines.append(notes)
    return "\n".join(lines)


def format_watchlist(wl: Watchlist) -> str:
    if not wl.entries:
        return "Watchlist is empty."
    return "\n\n".join(format_entry(e, i + 1) for i, e in enumerate(wl.entries))


def format_summary(wl: Watchlist) -> str:
    total = len(wl.entries)
    return f"Watchlist: {total} expression(s) monitored."
