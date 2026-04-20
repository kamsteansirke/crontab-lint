"""Reminder module: attach notes and due-dates to cron expressions."""
from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Optional


@dataclass
class Reminder:
    expression: str
    note: str
    due: Optional[str] = None          # ISO-8601 date string, e.g. "2025-12-31"
    tags: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def is_overdue(self) -> bool:
        """Return True if due date is set and is in the past (date-only comparison)."""
        if not self.due:
            return False
        try:
            due_date = datetime.fromisoformat(self.due).date()
            return due_date < datetime.utcnow().date()
        except ValueError:
            return False


class ReminderStore:
    def __init__(self, path: Path) -> None:
        self._path = path
        self._reminders: List[Reminder] = []
        if path.exists():
            self._load()

    # ------------------------------------------------------------------
    def add(self, reminder: Reminder) -> None:
        self._reminders.append(reminder)
        self._save()

    def remove(self, note: str) -> bool:
        before = len(self._reminders)
        self._reminders = [r for r in self._reminders if r.note != note]
        if len(self._reminders) < before:
            self._save()
            return True
        return False

    def all(self) -> List[Reminder]:
        return list(self._reminders)

    def find_by_expression(self, expression: str) -> List[Reminder]:
        return [r for r in self._reminders if r.expression == expression]

    def overdue(self) -> List[Reminder]:
        return [r for r in self._reminders if r.is_overdue()]

    # ------------------------------------------------------------------
    def _save(self) -> None:
        self._path.write_text(
            json.dumps([asdict(r) for r in self._reminders], indent=2)
        )

    def _load(self) -> None:
        data = json.loads(self._path.read_text())
        self._reminders = [Reminder(**d) for d in data]
