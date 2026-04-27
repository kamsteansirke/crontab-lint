"""Pause/resume tracking for cron expressions with optional reason and expiry."""
from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional


@dataclass
class PausedExpression:
    expression: str
    label: str
    reason: str = ""
    paused_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    resume_at: Optional[str] = None  # ISO-8601 or None

    def is_expired(self) -> bool:
        """Return True if resume_at is set and is in the past."""
        if self.resume_at is None:
            return False
        try:
            resume = datetime.fromisoformat(self.resume_at)
            now = datetime.now(timezone.utc)
            if resume.tzinfo is None:
                resume = resume.replace(tzinfo=timezone.utc)
            return now >= resume
        except ValueError:
            return False

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(d: dict) -> "PausedExpression":
        return PausedExpression(**d)


class PauseStore:
    def __init__(self, path: Path) -> None:
        self._path = path
        self._entries: List[PausedExpression] = self._load()

    def _load(self) -> List[PausedExpression]:
        if not self._path.exists():
            return []
        try:
            data = json.loads(self._path.read_text())
            return [PausedExpression.from_dict(d) for d in data]
        except (json.JSONDecodeError, TypeError, KeyError):
            return []

    def _save(self) -> None:
        self._path.write_text(json.dumps([e.to_dict() for e in self._entries], indent=2))

    def pause(self, entry: PausedExpression) -> None:
        self._entries = [e for e in self._entries if e.label != entry.label]
        self._entries.append(entry)
        self._save()

    def resume(self, label: str) -> bool:
        before = len(self._entries)
        self._entries = [e for e in self._entries if e.label != label]
        if len(self._entries) < before:
            self._save()
            return True
        return False

    def find(self, label: str) -> Optional[PausedExpression]:
        return next((e for e in self._entries if e.label == label), None)

    def all_active(self) -> List[PausedExpression]:
        """Return entries that are not expired."""
        return [e for e in self._entries if not e.is_expired()]

    def all(self) -> List[PausedExpression]:
        return list(self._entries)

    def purge_expired(self) -> int:
        before = len(self._entries)
        self._entries = [e for e in self._entries if not e.is_expired()]
        saved = before - len(self._entries)
        if saved:
            self._save()
        return saved
