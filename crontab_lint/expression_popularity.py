"""Track and rank crontab expression popularity based on usage frequency."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class PopularityEntry:
    expression: str
    count: int
    last_seen: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "expression": self.expression,
            "count": self.count,
            "last_seen": self.last_seen,
        }

    @staticmethod
    def from_dict(data: dict) -> "PopularityEntry":
        return PopularityEntry(
            expression=data["expression"],
            count=data.get("count", 0),
            last_seen=data.get("last_seen"),
        )


@dataclass
class PopularityReport:
    entries: List[PopularityEntry] = field(default_factory=list)

    def total_tracked(self) -> int:
        return len(self.entries)

    def top_n(self, n: int = 10) -> List[PopularityEntry]:
        return sorted(self.entries, key=lambda e: e.count, reverse=True)[:n]


class PopularityStore:
    def __init__(self, path: Path) -> None:
        self._path = path
        self._data: Dict[str, PopularityEntry] = {}
        self._load()

    def _load(self) -> None:
        if self._path.exists():
            raw = json.loads(self._path.read_text())
            for item in raw:
                entry = PopularityEntry.from_dict(item)
                self._data[entry.expression] = entry

    def _save(self) -> None:
        self._path.write_text(
            json.dumps([e.to_dict() for e in self._data.values()], indent=2)
        )

    def record(self, expression: str, timestamp: Optional[str] = None) -> PopularityEntry:
        if expression in self._data:
            self._data[expression].count += 1
            self._data[expression].last_seen = timestamp
        else:
            self._data[expression] = PopularityEntry(
                expression=expression, count=1, last_seen=timestamp
            )
        self._save()
        return self._data[expression]

    def get(self, expression: str) -> Optional[PopularityEntry]:
        return self._data.get(expression)

    def report(self) -> PopularityReport:
        return PopularityReport(entries=list(self._data.values()))

    def reset(self, expression: str) -> bool:
        if expression in self._data:
            del self._data[expression]
            self._save()
            return True
        return False
