"""Compute similarity between crontab expressions."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Tuple

from .parser import parse, ParseError
from .conflict_detector import _parse_field_values


@dataclass
class SimilarityResult:
    expression_a: str
    expression_b: str
    score: float          # 0.0 – 1.0
    field_scores: List[float] = field(default_factory=list)
    is_valid: bool = True
    error: str = ""


def _jaccard(a: set, b: set) -> float:
    """Jaccard similarity between two sets."""
    if not a and not b:
        return 1.0
    union = a | b
    if not union:
        return 1.0
    return len(a & b) / len(union)


def _field_set(values_str: str, min_val: int, max_val: int) -> set:
    """Return the set of concrete integer values for a cron field token."""
    return set(_parse_field_values(values_str, min_val, max_val))


# (field_index, min, max) for the five standard cron fields
_FIELD_RANGES = [
    (0, 0, 59),   # minute
    (1, 0, 23),   # hour
    (2, 1, 31),   # day-of-month
    (3, 1, 12),   # month
    (4, 0, 6),    # day-of-week
]


def compare(expr_a: str, expr_b: str) -> SimilarityResult:
    """Return a SimilarityResult comparing two cron expressions."""
    try:
        parsed_a = parse(expr_a)
        parsed_b = parse(expr_b)
    except ParseError as exc:
        return SimilarityResult(
            expression_a=expr_a,
            expression_b=expr_b,
            score=0.0,
            is_valid=False,
            error=str(exc),
        )

    fields_a = [
        parsed_a.minute,
        parsed_a.hour,
        parsed_a.day_of_month,
        parsed_a.month,
        parsed_a.day_of_week,
    ]
    fields_b = [
        parsed_b.minute,
        parsed_b.hour,
        parsed_b.day_of_month,
        parsed_b.month,
        parsed_b.day_of_week,
    ]

    field_scores: List[float] = []
    for (_, min_v, max_v), fa, fb in zip(_FIELD_RANGES, fields_a, fields_b):
        set_a = _field_set(fa, min_v, max_v)
        set_b = _field_set(fb, min_v, max_v)
        field_scores.append(_jaccard(set_a, set_b))

    overall = sum(field_scores) / len(field_scores) if field_scores else 0.0
    return SimilarityResult(
        expression_a=expr_a,
        expression_b=expr_b,
        score=round(overall, 4),
        field_scores=[round(s, 4) for s in field_scores],
    )


def rank_similar(
    target: str, candidates: List[str], top_n: int = 5
) -> List[Tuple[str, float]]:
    """Rank *candidates* by similarity to *target*, highest first."""
    results = [(c, compare(target, c).score) for c in candidates if c != target]
    results.sort(key=lambda x: x[1], reverse=True)
    return results[:top_n]
