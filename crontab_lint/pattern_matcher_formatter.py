"""Formatting helpers for pattern matcher results."""
from __future__ import annotations

from typing import List

from .pattern_matcher import MatchResult


def format_match(result: MatchResult, index: Optional[int] = None) -> str:  # noqa: F821
    prefix = f"{index}. " if index is not None else ""
    bar = _bar(result.score)
    return (
        f"{prefix}{result.expression}\n"
        f"  Explanation : {result.explanation}\n"
        f"  Match score : {bar} {result.score:.0%}"
    )


def format_matches(results: List[MatchResult], query: str = "") -> str:
    if not results:
        header = f'No matches found for "{query}".'
        return header
    lines = [f'Top matches for "{query}":' if query else "Matches:", ""]
    for i, r in enumerate(results, start=1):
        lines.append(format_match(r, index=i))
        lines.append("")
    return "\n".join(lines).rstrip()


def format_summary(results: List[MatchResult]) -> str:
    total = len(results)
    if total == 0:
        return "No pattern matches found."
    best = max(results, key=lambda r: r.score)
    return (
        f"{total} match(es) found. "
        f"Best: {best.expression!r} ({best.score:.0%})"
    )


def _bar(score: float, width: int = 10) -> str:
    filled = round(score * width)
    return "[" + "#" * filled + "-" * (width - filled) + "]"


# Fix missing import
from typing import Optional  # noqa: E402 (kept at bottom to match style of other formatters)
