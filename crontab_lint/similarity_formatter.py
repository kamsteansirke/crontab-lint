"""Format SimilarityResult objects for CLI output."""
from __future__ import annotations

from typing import List, Tuple

from .similarity import SimilarityResult

_FIELD_NAMES = ["minute", "hour", "day-of-month", "month", "day-of-week"]


def format_result(result: SimilarityResult, *, show_fields: bool = False) -> str:
    """Return a human-readable string for a single SimilarityResult."""
    if not result.is_valid:
        return (
            f"[ERROR] Cannot compare '{result.expression_a}' and "
            f"'{result.expression_b}': {result.error}"
        )

    pct = int(result.score * 100)
    lines = [
        f"  A : {result.expression_a}",
        f"  B : {result.expression_b}",
        f"  Similarity : {pct}%",
    ]

    if show_fields and result.field_scores:
        lines.append("  Field breakdown:")
        for name, fs in zip(_FIELD_NAMES, result.field_scores):
            bar = _bar(fs)
            lines.append(f"    {name:<14} {bar}  {int(fs * 100):>3}%")

    return "\n".join(lines)


def format_ranking(
    target: str,
    ranking: List[Tuple[str, float]],
) -> str:
    """Format a ranked list of similar expressions."""
    if not ranking:
        return f"No candidates to compare against '{target}'."

    lines = [f"Expressions most similar to: {target}"]
    for i, (expr, score) in enumerate(ranking, 1):
        pct = int(score * 100)
        bar = _bar(score)
        lines.append(f"  {i}. {bar}  {pct:>3}%  {expr}")
    return "\n".join(lines)


def format_summary(results: List[SimilarityResult]) -> str:
    """Return a one-line summary covering multiple comparisons."""
    valid = [r for r in results if r.is_valid]
    invalid = len(results) - len(valid)
    if not valid:
        return f"0 valid comparisons ({invalid} error(s))."
    avg = sum(r.score for r in valid) / len(valid)
    parts = [f"{len(valid)} comparison(s), avg similarity {int(avg * 100)}%"]
    if invalid:
        parts.append(f"{invalid} error(s) skipped")
    return ", ".join(parts) + "."


def _bar(score: float, width: int = 10) -> str:
    filled = round(score * width)
    return "[" + "#" * filled + "-" * (width - filled) + "]"
