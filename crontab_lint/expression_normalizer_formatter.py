"""Format NormalizeResult objects for CLI output."""
from __future__ import annotations
from typing import Iterable

from .expression_normalizer import NormalizeResult


def format_result(result: NormalizeResult, *, index: int | None = None) -> str:
    prefix = f"{index}. " if index is not None else ""
    if not result.ok:
        return f"{prefix}[ERROR] {result.original!r} — {result.error}"
    if result.changed:
        return (
            f"{prefix}[NORMALIZED]\n"
            f"  Original:   {result.original}\n"
            f"  Normalized: {result.normalized}"
        )
    return f"{prefix}[UNCHANGED] {result.original}"


def format_results(results: Iterable[NormalizeResult]) -> str:
    lines = []
    for i, r in enumerate(results, start=1):
        lines.append(format_result(r, index=i))
    return "\n".join(lines) if lines else "(no expressions)"


def format_summary(results: list[NormalizeResult]) -> str:
    total = len(results)
    errors = sum(1 for r in results if not r.ok)
    changed = sum(1 for r in results if r.ok and r.changed)
    unchanged = total - errors - changed
    return (
        f"Total: {total} | "
        f"Normalized: {changed} | "
        f"Unchanged: {unchanged} | "
        f"Errors: {errors}"
    )
