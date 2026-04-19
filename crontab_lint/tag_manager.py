"""Tag/label support for crontab expressions."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class TaggedExpression:
    expression: str
    tags: List[str] = field(default_factory=list)
    description: Optional[str] = None

    def has_tag(self, tag: str) -> bool:
        return tag in self.tags


@dataclass
class TagRegistry:
    entries: List[TaggedExpression] = field(default_factory=list)

    def add(self, expression: str, tags: List[str], description: Optional[str] = None) -> TaggedExpression:
        entry = TaggedExpression(expression=expression, tags=tags, description=description)
        self.entries.append(entry)
        return entry

    def find_by_tag(self, tag: str) -> List[TaggedExpression]:
        return [e for e in self.entries if e.has_tag(tag)]

    def all_tags(self) -> List[str]:
        seen = set()
        result = []
        for entry in self.entries:
            for tag in entry.tags:
                if tag not in seen:
                    seen.add(tag)
                    result.append(tag)
        return result

    def remove_by_expression(self, expression: str) -> int:
        before = len(self.entries)
        self.entries = [e for e in self.entries if e.expression != expression]
        return before - len(self.entries)


def from_dict(data: Dict) -> TaggedExpression:
    return TaggedExpression(
        expression=data["expression"],
        tags=data.get("tags", []),
        description=data.get("description"),
    )


def registry_from_list(items: List[Dict]) -> TagRegistry:
    reg = TagRegistry()
    for item in items:
        entry = from_dict(item)
        reg.entries.append(entry)
    return reg
