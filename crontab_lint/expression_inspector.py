"""Inspect a cron expression and return a structured breakdown of all its properties."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from .parser import parse, ParseError
from .explainer import explain
from .expression_tagger import auto_tag
from .frequency_analyzer import analyze
from .expression_scorer import score
from .complexity_analyzer import analyze as analyze_complexity
from .expression_cost_estimator import estimate


@dataclass
class InspectionResult:
    expression: str
    is_valid: bool
    error: Optional[str]
    explanation: Optional[str]
    tags: list[str]
    frequency_category: Optional[str]
    runs_per_day: Optional[float]
    score_total: Optional[int]
    score_grade: Optional[str]
    complexity_label: Optional[str]
    cost_level: Optional[str]
    notes: list[str] = field(default_factory=list)


def inspect(expression: str) -> InspectionResult:
    """Return a full inspection of a single cron expression."""
    expression = expression.strip()

    try:
        parse(expression)
        is_valid = True
        error = None
    except ParseError as exc:
        return InspectionResult(
            expression=expression,
            is_valid=False,
            error=str(exc),
            explanation=None,
            tags=[],
            frequency_category=None,
            runs_per_day=None,
            score_total=None,
            score_grade=None,
            complexity_label=None,
            cost_level=None,
        )

    explanation = explain(expression)

    tagging = auto_tag(expression)
    tags = tagging.tags if tagging.is_valid else []

    freq = analyze(expression)
    frequency_category = freq.category if freq.is_valid else None
    runs_per_day = freq.runs_per_day if freq.is_valid else None

    expr_score = score(expression)
    score_total = expr_score.total if expr_score.is_valid else None
    score_grade = expr_score.grade if expr_score.is_valid else None

    complexity = analyze_complexity(expression)
    complexity_label = complexity.label if complexity.is_valid else None

    cost = estimate(expression)
    cost_level = cost.cost_level if cost.is_valid else None
    notes = list(cost.notes) if cost.is_valid else []

    return InspectionResult(
        expression=expression,
        is_valid=is_valid,
        error=error,
        explanation=explanation,
        tags=tags,
        frequency_category=frequency_category,
        runs_per_day=runs_per_day,
        score_total=score_total,
        score_grade=score_grade,
        complexity_label=complexity_label,
        cost_level=cost_level,
        notes=notes,
    )
