"""Snapshot module: save and compare sets of crontab expressions."""
from __future__ import annotations
import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import List, Optional


@dataclass
class Snapshot:
    name: str
    expressions: List[str]
    created_at: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(d: dict) -> "Snapshot":
        return Snapshot(
            name=d["name"],
            expressions=d["expressions"],
            created_at=d.get("created_at", ""),
        )


@dataclass
class SnapshotStore:
    path: Path
    snapshots: List[Snapshot] = field(default_factory=list)

    def save(self) -> None:
        self.path.write_text(json.dumps([s.to_dict() for s in self.snapshots], indent=2))

    @staticmethod
    def load(path: Path) -> "SnapshotStore":
        store = SnapshotStore(path=path)
        if path.exists():
            data = json.loads(path.read_text())
            store.snapshots = [Snapshot.from_dict(d) for d in data]
        return store


def add(store: SnapshotStore, snapshot: Snapshot) -> None:
    store.snapshots = [s for s in store.snapshots if s.name != snapshot.name]
    store.snapshots.append(snapshot)
    store.save()


def find(store: SnapshotStore, name: str) -> Optional[Snapshot]:
    for s in store.snapshots:
        if s.name == name:
            return s
    return None


def remove(store: SnapshotStore, name: str) -> bool:
    before = len(store.snapshots)
    store.snapshots = [s for s in store.snapshots if s.name != name]
    if len(store.snapshots) < before:
        store.save()
        return True
    return False


def compare(old: Snapshot, new: Snapshot) -> dict:
    old_set = set(old.expressions)
    new_set = set(new.expressions)
    return {
        "added": sorted(new_set - old_set),
        "removed": sorted(old_set - new_set),
        "unchanged": sorted(old_set & new_set),
    }
