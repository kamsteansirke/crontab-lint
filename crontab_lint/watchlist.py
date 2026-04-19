"""Watchlist: track cron expressions to monitor for changes or issues."""
from __future__ import annotations
import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import List, Optional


@dataclass
class WatchedExpression:
    expression: str
    label: str
    notes: str = ""
    tags: List[str] = field(default_factory=list)

    def matches_label(self, label: str) -> bool:
        return self.label.lower() == label.lower()


@dataclass
class Watchlist:
    entries: List[WatchedExpression] = field(default_factory=list)


def add(wl: Watchlist, expr: str, label: str, notes: str = "", tags: Optional[List[str]] = None) -> WatchedExpression:
    we = WatchedExpression(expression=expr, label=label, notes=notes, tags=tags or [])
    wl.entries.append(we)
    return we


def remove(wl: Watchlist, label: str) -> bool:
    before = len(wl.entries)
    wl.entries = [e for e in wl.entries if not e.matches_label(label)]
    return len(wl.entries) < before


def find(wl: Watchlist, label: str) -> Optional[WatchedExpression]:
    for e in wl.entries:
        if e.matches_label(label):
            return e
    return None


def all_entries(wl: Watchlist) -> List[WatchedExpression]:
    return list(wl.entries)


def save(wl: Watchlist, path: Path) -> None:
    path.write_text(json.dumps([asdict(e) for e in wl.entries], indent=2))


def load(path: Path) -> Watchlist:
    if not path.exists():
        return Watchlist()
    data = json.loads(path.read_text())
    entries = [WatchedExpression(**d) for d in data]
    return Watchlist(entries=entries)
