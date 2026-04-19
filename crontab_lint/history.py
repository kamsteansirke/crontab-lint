"""Track and persist a history of linted crontab expressions."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Optional

DEFAULT_HISTORY_FILE = os.path.expanduser("~/.crontab_lint_history.json")


@dataclass
class HistoryEntry:
    expression: str
    valid: bool
    explanation: Optional[str]
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class History:
    entries: List[HistoryEntry] = field(default_factory=list)

    def add(self, entry: HistoryEntry) -> None:
        self.entries.append(entry)

    def recent(self, n: int = 10) -> List[HistoryEntry]:
        return self.entries[-n:]

    def clear(self) -> None:
        self.entries.clear()


def load(path: str = DEFAULT_HISTORY_FILE) -> History:
    if not os.path.exists(path):
        return History()
    with open(path, "r", encoding="utf-8") as fh:
        raw = json.load(fh)
    entries = [HistoryEntry(**e) for e in raw.get("entries", [])]
    return History(entries=entries)


def save(history: History, path: str = DEFAULT_HISTORY_FILE) -> None:
    data = {"entries": [asdict(e) for e in history.entries]}
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)


def record(expression: str, valid: bool, explanation: Optional[str] = None,
           path: str = DEFAULT_HISTORY_FILE) -> HistoryEntry:
    history = load(path)
    entry = HistoryEntry(expression=expression, valid=valid, explanation=explanation)
    history.add(entry)
    save(history, path)
    return entry
