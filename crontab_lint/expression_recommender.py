"""Suggest similar or improved crontab expressions based on a natural-language query or existing expression."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from crontab_lint.parser import parse, ParseError
from crontab_lint.explainer import explain
from crontab_lint.template_library import list_templates, Template


@dataclass
class Recommendation:
    expression: str
    explanation: str
    reason: str
    score: float  # 0.0 – 1.0


@dataclass
class RecommendationResult:
    query: str
    recommendations: List[Recommendation] = field(default_factory=list)
    error: Optional[str] = None

    @property
    def has_results(self) -> bool:
        return bool(self.recommendations)


_KEYWORD_MAP = {
    "minute": ["* * * * *", "*/5 * * * *", "*/15 * * * *", "*/30 * * * *"],
    "hourly": ["@hourly", "0 * * * *"],
    "daily": ["@daily", "0 0 * * *", "0 6 * * *", "0 9 * * *"],
    "midnight": ["@midnight", "0 0 * * *"],
    "weekly": ["@weekly", "0 0 * * 0", "0 9 * * 1"],
    "monthly": ["@monthly", "0 0 1 * *", "0 9 1 * *"],
    "yearly": ["@yearly", "@annually", "0 0 1 1 *"],
    "reboot": ["@reboot"],
    "weekday": ["0 9 * * 1-5", "0 17 * * 1-5"],
    "weekend": ["0 10 * * 6,0", "0 0 * * 6"],
    "morning": ["0 6 * * *", "0 7 * * *", "0 8 * * *", "0 9 * * *"],
    "evening": ["0 18 * * *", "0 20 * * *", "0 22 * * *"],
    "night": ["0 23 * * *", "0 0 * * *", "0 1 * * *"],
    "backup": ["0 2 * * *", "0 3 * * 0", "0 1 1 * *"],
    "cleanup": ["0 4 * * *", "0 3 * * 0"],
}


def _score_template(template: Template, query: str) -> float:
    q = query.lower()
    hits = sum(1 for kw in template.tags if kw in q)
    if template.name.lower() in q:
        hits += 2
    return min(hits / max(len(template.tags), 1), 1.0)


def recommend(query: str, top_n: int = 5) -> RecommendationResult:
    """Return up to *top_n* expression recommendations for *query*."""
    if not query or not query.strip():
        return RecommendationResult(query=query, error="Query must not be empty.")

    q = query.strip().lower()
    candidates: List[Recommendation] = []

    # Keyword-based candidates
    for keyword, expressions in _KEYWORD_MAP.items():
        if keyword in q:
            for expr in expressions:
                try:
                    parsed = parse(expr)
                    explanation = explain(parsed)
                except ParseError:
                    explanation = expr
                candidates.append(
                    Recommendation(
                        expression=expr,
                        explanation=explanation,
                        reason=f"Matches keyword '{keyword}'",
                        score=0.6,
                    )
                )

    # Template-based candidates
    for tmpl in list_templates():
        sc = _score_template(tmpl, q)
        if sc > 0:
            try:
                parsed = parse(tmpl.expression)
                explanation = explain(parsed)
            except ParseError:
                explanation = tmpl.expression
            candidates.append(
                Recommendation(
                    expression=tmpl.expression,
                    explanation=explanation,
                    reason=f"Template: {tmpl.name}",
                    score=sc,
                )
            )

    # Deduplicate by expression, keeping highest score
    seen: dict[str, Recommendation] = {}
    for rec in candidates:
        if rec.expression not in seen or rec.score > seen[rec.expression].score:
            seen[rec.expression] = rec

    ranked = sorted(seen.values(), key=lambda r: r.score, reverse=True)[:top_n]

    if not ranked:
        return RecommendationResult(query=query, error="No recommendations found for the given query.")

    return RecommendationResult(query=query, recommendations=ranked)
