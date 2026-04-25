"""Search crontab expressions by keyword, tag, or schedule pattern."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from crontab_lint.parser import parse, ParseError
from crontab_lint.explainer import explain


@dataclass
class SearchResult:
    expression: str
    explanation: Optional[str]
    matched_on: str  # 'expression', 'explanation', or 'tag'
    tags: List[str] = field(default_factory=list)


@dataclass
class SearchReport:
    query: str
    results: List[SearchResult] = field(default_factory=list)

    @property
    def has_results(self) -> bool:
        return len(self.results) > 0

    @property
    def count(self) -> int:
        return len(self.results)


def _safe_explain(expression: str) -> Optional[str]:
    try:
        parsed = parse(expression)
        return explain(parsed)
    except (ParseError, Exception):
        return None


def _safe_tags(expression: str) -> List[str]:
    """Return auto-tags for an expression without raising."""
    try:
        from crontab_lint.expression_tagger import auto_tag
        result = auto_tag(expression)
        return result.tags if result.valid else []
    except Exception:
        return []


def search(
    expressions: List[str],
    query: str,
    *,
    search_explanations: bool = True,
    search_tags: bool = True,
) -> SearchReport:
    """Search *expressions* for those matching *query*.

    Matching is case-insensitive substring search over:
    - the raw expression string
    - the human-readable explanation (if *search_explanations* is True)
    - auto-generated tags (if *search_tags* is True)
    """
    query_lower = query.strip().lower()
    report = SearchReport(query=query)

    if not query_lower:
        return report

    for raw in expressions:
        line = raw.strip()
        if not line or line.startswith("#"):
            continue

        matched_on: Optional[str] = None

        if query_lower in line.lower():
            matched_on = "expression"

        explanation: Optional[str] = None
        if matched_on is None and search_explanations:
            explanation = _safe_explain(line)
            if explanation and query_lower in explanation.lower():
                matched_on = "explanation"

        tags: List[str] = []
        if matched_on is None and search_tags:
            tags = _safe_tags(line)
            if any(query_lower in t.lower() for t in tags):
                matched_on = "tag"

        if matched_on is not None:
            if explanation is None:
                explanation = _safe_explain(line)
            if not tags:
                tags = _safe_tags(line)
            report.results.append(
                SearchResult(
                    expression=line,
                    explanation=explanation,
                    matched_on=matched_on,
                    tags=tags,
                )
            )

    return report
