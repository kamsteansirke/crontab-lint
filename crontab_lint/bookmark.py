"""Bookmark manager for saving favorite cron expressions."""
from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import List, Optional

DEFAULT_PATH = Path.home() / ".crontab_lint_bookmarks.json"


@dataclass
class Bookmark:
    expression: str
    label: str
    notes: str = ""

    def matches_label(self, label: str) -> bool:
        return self.label.lower() == label.lower()


@dataclass
class BookmarkStore:
    bookmarks: List[Bookmark] = field(default_factory=list)

    def add(self, expression: str, label: str, notes: str = "") -> Bookmark:
        bm = Bookmark(expression=expression, label=label, notes=notes)
        self.bookmarks.append(bm)
        return bm

    def remove(self, label: str) -> bool:
        before = len(self.bookmarks)
        self.bookmarks = [b for b in self.bookmarks if not b.matches_label(label)]
        return len(self.bookmarks) < before

    def find(self, label: str) -> Optional[Bookmark]:
        for b in self.bookmarks:
            if b.matches_label(label):
                return b
        return None

    def all(self) -> List[Bookmark]:
        return list(self.bookmarks)


def load(path: Path = DEFAULT_PATH) -> BookmarkStore:
    if not path.exists():
        return BookmarkStore()
    data = json.loads(path.read_text())
    return BookmarkStore(bookmarks=[Bookmark(**b) for b in data.get("bookmarks", [])])


def save(store: BookmarkStore, path: Path = DEFAULT_PATH) -> None:
    path.write_text(json.dumps({"bookmarks": [asdict(b) for b in store.bookmarks]}, indent=2))
