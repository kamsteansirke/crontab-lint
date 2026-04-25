"""Expression alias manager: map short names to cron expressions."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import json
import os


@dataclass
class Alias:
    name: str
    expression: str
    description: str = ""

    def to_dict(self) -> dict:
        return {"name": self.name, "expression": self.expression, "description": self.description}

    @staticmethod
    def from_dict(data: dict) -> "Alias":
        return Alias(
            name=data["name"],
            expression=data["expression"],
            description=data.get("description", ""),
        )


@dataclass
class AliasStore:
    _aliases: Dict[str, Alias] = field(default_factory=dict)

    def add(self, alias: Alias) -> None:
        self._aliases[alias.name] = alias

    def remove(self, name: str) -> bool:
        if name in self._aliases:
            del self._aliases[name]
            return True
        return False

    def find(self, name: str) -> Optional[Alias]:
        return self._aliases.get(name)

    def all(self) -> List[Alias]:
        return list(self._aliases.values())

    def search(self, query: str) -> List[Alias]:
        q = query.lower()
        return [
            a for a in self._aliases.values()
            if q in a.name.lower() or q in a.description.lower()
        ]

    def save(self, path: str) -> None:
        with open(path, "w") as fh:
            json.dump([a.to_dict() for a in self._aliases.values()], fh, indent=2)

    @staticmethod
    def load(path: str) -> "AliasStore":
        store = AliasStore()
        if not os.path.exists(path):
            return store
        with open(path) as fh:
            for item in json.load(fh):
                store.add(Alias.from_dict(item))
        return store
