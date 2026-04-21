"""Pattern matcher: find cron expressions matching a natural-language pattern."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .parser import parse, ParseError
from .explainer import explain


@dataclass
class MatchResult:
    expression: str
    explanation: str
    score: float  # 0.0 – 1.0, higher = better match


_KEYWORD_MAP: dict[str, List[str]] = {
    "minute": ["* * * * *", "*/1 * * * *"],
    "hourly": ["@hourly", "0 * * * *"],
    "daily": ["@daily", "0 0 * * *"],
    "midnight": ["0 0 * * *", "@midnight"],
    "weekly": ["@weekly", "0 0 * * 0"],
    "monthly": ["@monthly", "0 0 1 * *"],
    "yearly": ["@yearly", "0 0 1 1 *"],
    "monday": ["0 0 * * 1", "0 9 * * 1"],
    "friday": ["0 0 * * 5", "0 9 * * 5"],
    "weekend": ["0 0 * * 6,0", "0 0 * * 6-0"],
    "noon": ["0 12 * * *"],
    "morning": ["0 9 * * *", "0 8 * * *"],
    "night": ["0 22 * * *", "0 23 * * *"],
    "backup": ["0 2 * * *", "0 3 * * 0"],
    "cleanup": ["0 4 * * *", "0 0 * * 0"],
}


def _score(query_words: List[str], keywords: List[str]) -> float:
    """Return fraction of query words that appear in keywords."""
    if not query_words:
        return 0.0
    hits = sum(1 for w in query_words if any(w in k for k in keywords))
    return hits / len(query_words)


def match(query: str, top_n: int = 5) -> List[MatchResult]:
    """Return up to *top_n* cron expressions that best match *query*."""
    words = [w.lower().strip(".,!?") for w in query.split()]
    seen: dict[str, float] = {}

    for keyword, expressions in _KEYWORD_MAP.items():
        s = _score(words, [keyword])
        if s == 0.0:
            continue
        for expr in expressions:
            seen[expr] = max(seen.get(expr, 0.0), s)

    ranked = sorted(seen.items(), key=lambda kv: kv[1], reverse=True)[:top_n]

    results: List[MatchResult] = []
    for expr, sc in ranked:
        try:
            parsed = parse(expr)
            exp = explain(parsed)
        except (ParseError, Exception):
            continue
        results.append(MatchResult(expression=expr, explanation=exp, score=round(sc, 3)))
    return results


def best_match(query: str) -> Optional[MatchResult]:
    """Return the single best matching expression, or None."""
    results = match(query, top_n=1)
    return results[0] if results else None
