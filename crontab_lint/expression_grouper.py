"""Group cron expressions by shared schedule characteristics."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .parser import parse, ParseError
from .frequency_analyzer import analyze


@dataclass
class ExpressionGroup:
    label: str
    category: str
    expressions: List[str] = field(default_factory=list)

    def size(self) -> int:
        return len(self.expressions)


@dataclass
class GroupingResult:
    groups: List[ExpressionGroup]
    ungrouped: List[str]

    def group_count(self) -> int:
        return len(self.groups)

    def find(self, category: str) -> Optional[ExpressionGroup]:
        for g in self.groups:
            if g.category == category:
                return g
        return None


def _get_category(expression: str) -> Optional[str]:
    """Return a category string for a valid expression, or None on error."""
    try:
        parse(expression)
    except ParseError:
        return None
    try:
        analysis = analyze(expression)
        if not analysis.valid:
            return None
        return analysis.category
    except Exception:
        return None


def group(expressions: List[str]) -> GroupingResult:
    """Group expressions by frequency category."""
    buckets: Dict[str, ExpressionGroup] = {}
    ungrouped: List[str] = []

    for expr in expressions:
        expr = expr.strip()
        if not expr or expr.startswith("#"):
            continue
        category = _get_category(expr)
        if category is None:
            ungrouped.append(expr)
            continue
        if category not in buckets:
            label = category.replace("_", " ").title()
            buckets[category] = ExpressionGroup(label=label, category=category)
        buckets[category].expressions.append(expr)

    groups = sorted(buckets.values(), key=lambda g: g.label)
    return GroupingResult(groups=groups, ungrouped=ungrouped)
