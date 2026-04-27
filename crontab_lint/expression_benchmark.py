"""Benchmark multiple cron expressions by frequency and cost."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .parser import parse, ParseError
from .frequency_analyzer import analyze
from .expression_cost_estimator import estimate


@dataclass
class BenchmarkEntry:
    expression: str
    is_valid: bool
    error: Optional[str]
    runs_per_day: float
    cost_level: str
    frequency_category: str
    rank: int = 0


@dataclass
class BenchmarkReport:
    entries: List[BenchmarkEntry] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.entries)

    @property
    def valid_count(self) -> int:
        return sum(1 for e in self.entries if e.is_valid)

    @property
    def invalid_count(self) -> int:
        return self.total - self.valid_count


def benchmark(expressions: List[str]) -> BenchmarkReport:
    """Benchmark a list of cron expressions."""
    entries: List[BenchmarkEntry] = []

    for raw in expressions:
        expr = raw.strip()
        if not expr or expr.startswith("#"):
            continue

        try:
            parse(expr)
            is_valid = True
            error = None
        except ParseError as exc:
            is_valid = False
            error = str(exc)

        freq = analyze(expr)
        cost = estimate(expr)

        entries.append(
            BenchmarkEntry(
                expression=expr,
                is_valid=is_valid,
                error=error,
                runs_per_day=freq.runs_per_day if freq.is_valid else 0.0,
                cost_level=cost.cost_level if cost.is_valid else "unknown",
                frequency_category=freq.category if freq.is_valid else "invalid",
            )
        )

    # Rank valid entries by runs_per_day descending
    valid = sorted(
        [e for e in entries if e.is_valid],
        key=lambda e: e.runs_per_day,
        reverse=True,
    )
    for i, entry in enumerate(valid, start=1):
        entry.rank = i

    return BenchmarkReport(entries=entries)
