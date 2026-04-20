"""Audit log for tracking crontab expression changes and lint actions."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import List, Optional


@dataclass
class AuditEntry:
    action: str          # e.g. "lint", "add", "remove", "edit"
    expression: str
    actor: Optional[str]  # username or label
    detail: Optional[str]
    timestamp: str

    @staticmethod
    def create(
        action: str,
        expression: str,
        actor: Optional[str] = None,
        detail: Optional[str] = None,
    ) -> "AuditEntry":
        ts = datetime.now(timezone.utc).isoformat()
        return AuditEntry(
            action=action,
            expression=expression,
            actor=actor,
            detail=detail,
            timestamp=ts,
        )


class AuditLog:
    def __init__(self, path: str) -> None:
        self.path = path
        self._entries: List[AuditEntry] = []
        if os.path.exists(path):
            self._load()

    def _load(self) -> None:
        with open(self.path, "r", encoding="utf-8") as fh:
            raw = json.load(fh)
        self._entries = [AuditEntry(**r) for r in raw]

    def _save(self) -> None:
        with open(self.path, "w", encoding="utf-8") as fh:
            json.dump([asdict(e) for e in self._entries], fh, indent=2)

    def record(self, entry: AuditEntry) -> None:
        self._entries.append(entry)
        self._save()

    def recent(self, n: int = 20) -> List[AuditEntry]:
        return self._entries[-n:]

    def filter_by_action(self, action: str) -> List[AuditEntry]:
        return [e for e in self._entries if e.action == action]

    def filter_by_actor(self, actor: str) -> List[AuditEntry]:
        return [e for e in self._entries if e.actor == actor]

    def clear(self) -> None:
        self._entries = []
        self._save()

    def __len__(self) -> int:
        return len(self._entries)
