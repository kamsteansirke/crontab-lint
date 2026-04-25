"""Compute aggregate statistics over a collection of crontab expressions."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict

from .parser import parse, ParseError
from .frequency_analyzer import analyze, FrequencyAnalysis


@dataclass
class ExpressionStatistics:
    total: int = 0
    valid: int = 0
    invalid: int = 0
    category_counts: Dict[str, int] = field(default_factory=dict)
    most_common_category: str = ""
    invalid_expressions: List[str] = field(default_factory=list)

    @property
    def valid_ratio(self) -> float:
        if self.total == 0:
            return 0.0
        return self.valid / self.total


def compute(lines: List[str]) -> ExpressionStatistics:
    """Compute statistics from a list of raw crontab lines."""
    stats = ExpressionStatistics()

    for raw in lines:
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue

        stats.total += 1

        try:
            expr = parse(stripped)
        except ParseError:
            stats.invalid += 1
            stats.invalid_expressions.append(stripped)
            continue

        stats.valid += 1
        analysis: FrequencyAnalysis = analyze(stripped)
        if analysis.valid:
            cat = analysis.category
            stats.category_counts[cat] = stats.category_counts.get(cat, 0) + 1

    if stats.category_counts:
        stats.most_common_category = max(
            stats.category_counts, key=lambda k: stats.category_counts[k]
        )

    return stats
