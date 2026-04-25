"""Classify crontab expressions into human-readable categories."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .parser import parse, ParseError
from .frequency_analyzer import analyze


@dataclass
class ClassificationResult:
    expression: str
    is_valid: bool
    category: Optional[str]
    subcategory: Optional[str]
    labels: List[str] = field(default_factory=list)
    error: Optional[str] = None


def classify(expression: str) -> ClassificationResult:
    """Classify a crontab expression."""
    try:
        parse(expression)
    except ParseError as exc:
        return ClassificationResult(
            expression=expression,
            is_valid=False,
            category=None,
            subcategory=None,
            error=str(exc),
        )

    analysis = analyze(expression)
    if not analysis.is_valid:
        return ClassificationResult(
            expression=expression,
            is_valid=False,
            category=None,
            subcategory=None,
            error="Invalid expression",
        )

    category, subcategory, labels = _derive_classification(expression, analysis)
    return ClassificationResult(
        expression=expression,
        is_valid=True,
        category=category,
        subcategory=subcategory,
        labels=labels,
    )


def _derive_classification(expression: str, analysis):
    """Return (category, subcategory, labels) based on frequency analysis."""
    labels: List[str] = []
    cat = analysis.category  # e.g. 'high', 'medium', 'low', 'rare'
    runs = analysis.runs_per_day

    if runs >= 1440:
        category = "real-time"
        subcategory = "every-minute"
        labels.append("high-frequency")
    elif runs >= 60:
        category = "frequent"
        subcategory = "sub-hourly"
        labels.append("high-frequency")
    elif runs >= 24:
        category = "frequent"
        subcategory = "hourly"
        labels.append("medium-frequency")
    elif runs >= 2:
        category = "periodic"
        subcategory = "multiple-daily"
        labels.append("medium-frequency")
    elif runs == 1:
        category = "scheduled"
        subcategory = "once-daily"
        labels.append("low-frequency")
    else:
        category = "rare"
        subcategory = "sub-daily"
        labels.append("rare")

    if cat:
        labels.append(cat)

    return category, subcategory, labels


def classify_many(expressions: List[str]) -> List[ClassificationResult]:
    """Classify a list of expressions, skipping blanks and comments."""
    results = []
    for line in expressions:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        results.append(classify(stripped))
    return results
