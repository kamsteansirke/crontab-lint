"""Detect and report duplicate or equivalent crontab expressions."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Tuple

from .parser import parse, ParseError
from .expression_normalizer import normalize


@dataclass
class DuplicateGroup:
    """A group of expressions that are considered equivalent."""
    canonical: str
    expressions: List[str] = field(default_factory=list)

    @property
    def size(self) -> int:
        return len(self.expressions)

    @property
    def is_duplicate(self) -> bool:
        return self.size > 1


@dataclass
class DeduplicationResult:
    """Result of deduplication analysis over a list of expressions."""
    groups: List[DuplicateGroup] = field(default_factory=list)
    invalid: List[str] = field(default_factory=list)

    @property
    def duplicate_groups(self) -> List[DuplicateGroup]:
        return [g for g in self.groups if g.is_duplicate]

    @property
    def has_duplicates(self) -> bool:
        return any(g.is_duplicate for g in self.groups)

    @property
    def duplicate_count(self) -> int:
        return sum(g.size - 1 for g in self.duplicate_groups)

    @property
    def unique_count(self) -> int:
        return len(self.groups)


def _canonical_key(expression: str) -> str:
    """Return a stable key for grouping equivalent expressions."""
    result = normalize(expression)
    if result.ok:
        return result.normalized
    return expression.strip()


def deduplicate(expressions: List[str]) -> DeduplicationResult:
    """Group expressions by equivalence and identify duplicates."""
    groups: Dict[str, DuplicateGroup] = {}
    invalid: List[str] = []

    for expr in expressions:
        stripped = expr.strip()
        if not stripped or stripped.startswith("#"):
            continue
        try:
            parse(stripped)
        except ParseError:
            invalid.append(stripped)
            continue

        key = _canonical_key(stripped)
        if key not in groups:
            groups[key] = DuplicateGroup(canonical=key)
        groups[key].expressions.append(stripped)

    return DeduplicationResult(
        groups=list(groups.values()),
        invalid=invalid,
    )
