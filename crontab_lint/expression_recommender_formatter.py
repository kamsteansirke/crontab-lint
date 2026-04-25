"""Format RecommendationResult objects for CLI output."""
from __future__ import annotations

from typing import List

from crontab_lint.expression_recommender import Recommendation, RecommendationResult


def format_recommendation(rec: Recommendation, index: Optional[int] = None) -> str:
    """Format a single Recommendation as a human-readable string."""
    prefix = f"{index}. " if index is not None else "  "
    lines = [
        f"{prefix}{rec.expression}",
        f"     Explanation : {rec.explanation}",
        f"     Reason      : {rec.reason}",
        f"     Score       : {rec.score:.2f}",
    ]
    return "\n".join(lines)


def format_result(result: RecommendationResult) -> str:
    """Format a full RecommendationResult."""
    lines: List[str] = [f"Recommendations for: \"{result.query}\""]
    lines.append("-" * 50)

    if result.error:
        lines.append(f"[!] {result.error}")
        return "\n".join(lines)

    if not result.has_results:
        lines.append("No recommendations found.")
        return "\n".join(lines)

    for i, rec in enumerate(result.recommendations, start=1):
        lines.append(format_recommendation(rec, index=i))

    return "\n".join(lines)


def format_summary(results: List[RecommendationResult]) -> str:
    """Format a brief summary line for multiple recommendation results."""
    total = len(results)
    with_results = sum(1 for r in results if r.has_results)
    errors = sum(1 for r in results if r.error)
    parts = [
        f"Queries: {total}",
        f"With results: {with_results}",
        f"Errors: {errors}",
    ]
    return "Summary — " + " | ".join(parts)


# Fix missing import
from typing import Optional  # noqa: E402  (moved to top in real code)
