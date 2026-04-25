"""Formatters for expression tagging results."""
from __future__ import annotations

from typing import List

from crontab_lint.expression_tagger import TaggingResult


def format_result(result: TaggingResult, index: int | None = None) -> str:
    prefix = f"{index}. " if index is not None else ""
    if not result.is_valid:
        return f"{prefix}[INVALID] {result.expression}  error: {result.error}"
    tags_str = ", ".join(result.tags) if result.tags else "(none)"
    return f"{prefix}{result.expression}\n  tags: {tags_str}"


def format_results(results: List[TaggingResult], *, numbered: bool = False) -> str:
    if not results:
        return "No expressions to tag."
    lines: List[str] = []
    for i, r in enumerate(results, 1):
        idx = i if numbered else None
        lines.append(format_result(r, index=idx))
    return "\n".join(lines)


def format_summary(results: List[TaggingResult]) -> str:
    total = len(results)
    valid = sum(1 for r in results if r.is_valid)
    invalid = total - valid
    all_tags: List[str] = []
    for r in results:
        all_tags.extend(r.tags)
    unique_tags = sorted(set(all_tags))
    tag_line = ", ".join(unique_tags) if unique_tags else "(none)"
    return (
        f"Total: {total} | Valid: {valid} | Invalid: {invalid}\n"
        f"Unique tags: {tag_line}"
    )
