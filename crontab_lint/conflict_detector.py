"""Detect conflicts and overlaps between multiple cron expressions."""

from dataclasses import dataclass, field
from typing import List, Tuple
from .parser import CronExpression


@dataclass
class Conflict:
    expression_a: str
    expression_b: str
    reason: str


@dataclass
class ConflictReport:
    conflicts: List[Conflict] = field(default_factory=list)

    @property
    def has_conflicts(self) -> bool:
        return len(self.conflicts) > 0


def _parse_field_values(field_str: str, min_val: int, max_val: int) -> set:
    """Expand a cron field string into a set of integer values."""
    values = set()
    all_values = set(range(min_val, max_val + 1))

    for part in field_str.split(","):
        if part == "*":
            return all_values
        elif "/" in part:
            base, step = part.split("/", 1)
            step = int(step)
            start = min_val if base == "*" else int(base)
            values.update(range(start, max_val + 1, step))
        elif "-" in part:
            lo, hi = part.split("-", 1)
            values.update(range(int(lo), int(hi) + 1))
        else:
            values.add(int(part))

    return values


def _expressions_overlap(a: CronExpression, b: CronExpression) -> bool:
    """Return True if two cron expressions can fire at the same time."""
    ranges = [
        (a.minute, b.minute, 0, 59),
        (a.hour, b.hour, 0, 23),
        (a.day_of_month, b.day_of_month, 1, 31),
        (a.month, b.month, 1, 12),
        (a.day_of_week, b.day_of_week, 0, 6),
    ]
    for fa, fb, lo, hi in ranges:
        va = _parse_field_values(fa, lo, hi)
        vb = _parse_field_values(fb, lo, hi)
        if not va.intersection(vb):
            return False
    return True


def detect_conflicts(expressions: List[Tuple[str, CronExpression]]) -> ConflictReport:
    """Check all pairs of expressions for scheduling conflicts."""
    report = ConflictReport()
    items = list(expressions)
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            raw_a, expr_a = items[i]
            raw_b, expr_b = items[j]
            if _expressions_overlap(expr_a, expr_b):
                report.conflicts.append(
                    Conflict(
                        expression_a=raw_a,
                        expression_b=raw_b,
                        reason="Expressions can fire at the same time",
                    )
                )
    return report
