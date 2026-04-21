"""Format ExpressionScore objects for terminal output."""
from __future__ import annotations

from typing import List

from .expression_scorer import ExpressionScore


def format_score(result: ExpressionScore, *, show_details: bool = True) -> str:
    lines: List[str] = []
    lines.append(f"Expression : {result.expression}")
    if not result.valid:
        lines.append(f"  [INVALID] {result.error}")
        lines.append(f"  Grade     : F")
        return "\n".join(lines)

    lines.append(f"  Score     : {result.total}/{result.max_score}")
    lines.append(f"  Grade     : {result.grade}")

    if show_details and result.details:
        lines.append("  Breakdown :")
        for detail in result.details:
            sign = "+" if detail.points >= 0 else ""
            lines.append(f"    [{detail.category}] {detail.message} ({sign}{detail.points})")

    return "\n".join(lines)


def format_scores(results: List[ExpressionScore], *, show_details: bool = True) -> str:
    parts = [format_score(r, show_details=show_details) for r in results]
    return "\n\n".join(parts)


def format_summary(results: List[ExpressionScore]) -> str:
    if not results:
        return "No expressions scored."
    valid = [r for r in results if r.valid]
    avg = sum(r.total for r in valid) / len(valid) if valid else 0
    grade_counts: dict[str, int] = {}
    for r in results:
        grade_counts[r.grade] = grade_counts.get(r.grade, 0) + 1
    lines = [
        f"Scored {len(results)} expression(s), {len(valid)} valid.",
        f"Average score: {avg:.1f}/{results[0].max_score if results else 100}",
        "Grade distribution: "
        + ", ".join(f"{g}:{c}" for g, c in sorted(grade_counts.items())),
    ]
    return "\n".join(lines)
