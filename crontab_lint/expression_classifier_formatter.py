"""Formatters for ClassificationResult."""
from __future__ import annotations

from typing import List

from .expression_classifier import ClassificationResult

_CHECK = "\u2714"
_CROSS = "\u2718"


def format_result(result: ClassificationResult, index: int | None = None) -> str:
    """Format a single ClassificationResult as a human-readable string."""
    prefix = f"{index}. " if index is not None else ""
    if not result.is_valid:
        return (
            f"{prefix}{_CROSS} {result.expression}\n"
            f"   Error: {result.error}"
        )

    labels_str = ", ".join(result.labels) if result.labels else "none"
    lines = [
        f"{prefix}{_CHECK} {result.expression}",
        f"   Category    : {result.category}",
        f"   Subcategory : {result.subcategory}",
        f"   Labels      : {labels_str}",
    ]
    return "\n".join(lines)


def format_results(results: List[ClassificationResult]) -> str:
    """Format multiple ClassificationResults."""
    if not results:
        return "No expressions to classify."
    parts = [format_result(r, index=i + 1) for i, r in enumerate(results)]
    return "\n\n".join(parts)


def format_summary(results: List[ClassificationResult]) -> str:
    """Return a short summary line for a list of results."""
    total = len(results)
    valid = sum(1 for r in results if r.is_valid)
    invalid = total - valid

    from collections import Counter
    category_counts: Counter = Counter(
        r.category for r in results if r.is_valid and r.category
    )
    top = category_counts.most_common(3)
    top_str = ", ".join(f"{cat}={n}" for cat, n in top)

    parts = [
        f"Total: {total}",
        f"Valid: {valid}",
        f"Invalid: {invalid}",
    ]
    if top_str:
        parts.append(f"Top categories: {top_str}")
    return " | ".join(parts)
