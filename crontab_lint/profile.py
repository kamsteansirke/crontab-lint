"""Named profiles for grouping and reusing cron validation settings."""
from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import List, Optional


@dataclass
class Profile:
    name: str
    description: str = ""
    expressions: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)

    def add_expression(self, expr: str) -> None:
        if expr not in self.expressions:
            self.expressions.append(expr)

    def remove_expression(self, expr: str) -> bool:
        if expr in self.expressions:
            self.expressions.remove(expr)
            return True
        return False

    def has_tag(self, tag: str) -> bool:
        return tag in self.tags


class ProfileStore:
    def __init__(self, path: Path) -> None:
        self._path = path
        self._profiles: List[Profile] = self._load()

    def _load(self) -> List[Profile]:
        if not self._path.exists():
            return []
        data = json.loads(self._path.read_text())
        return [Profile(**p) for p in data]

    def _save(self) -> None:
        self._path.write_text(json.dumps([asdict(p) for p in self._profiles], indent=2))

    def add(self, profile: Profile) -> None:
        self._profiles = [p for p in self._profiles if p.name != profile.name]
        self._profiles.append(profile)
        self._save()

    def remove(self, name: str) -> bool:
        before = len(self._profiles)
        self._profiles = [p for p in self._profiles if p.name != name]
        if len(self._profiles) < before:
            self._save()
            return True
        return False

    def find(self, name: str) -> Optional[Profile]:
        return next((p for p in self._profiles if p.name == name), None)

    def all(self) -> List[Profile]:
        return list(self._profiles)

    def find_by_tag(self, tag: str) -> List[Profile]:
        return [p for p in self._profiles if p.has_tag(tag)]
