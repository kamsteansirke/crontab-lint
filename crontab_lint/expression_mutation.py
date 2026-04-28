"""Expression mutation: generate variants of a cron expression by tweaking fields.

Useful for exploring nearby schedules, testing edge cases, or suggesting
alternatives when a user wants a slightly different frequency.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .parser import parse, ParseError
from .explainer import explain


@dataclass
class MutationVariant:
    """A single mutated variant of an original expression."""

    expression: str
    field_name: str          # which field was mutated
    description: str         # human-readable description of the change
    explanation: Optional[str] = None
    is_valid: bool = True


@dataclass
class MutationResult:
    """Result of mutating a cron expression."""

    original: str
    is_valid: bool
    error: Optional[str] = None
    variants: List[MutationVariant] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.variants)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

_FIELD_NAMES = ["minute", "hour", "day_of_month", "month", "day_of_week"]


def _replace_field(parts: List[str], index: int, value: str) -> str:
    """Return a new expression string with one field replaced."""
    new_parts = list(parts)
    new_parts[index] = value
    return " ".join(new_parts)


def _make_variant(
    parts: List[str],
    index: int,
    new_value: str,
    description: str,
) -> Optional[MutationVariant]:
    """Build a MutationVariant, validating the resulting expression."""
    expr = _replace_field(parts, index, new_value)
    field_name = _FIELD_NAMES[index]
    try:
        parse(expr)
        exp = explain(expr)
        return MutationVariant(
            expression=expr,
            field_name=field_name,
            description=description,
            explanation=exp,
            is_valid=True,
        )
    except (ParseError, Exception):
        return MutationVariant(
            expression=expr,
            field_name=field_name,
            description=description,
            explanation=None,
            is_valid=False,
        )


# ---------------------------------------------------------------------------
# Mutation strategies
# ---------------------------------------------------------------------------

def _minute_mutations(parts: List[str]) -> List[MutationVariant]:
    current = parts[0]
    mutations = []
    if current != "*":
        mutations.append(_make_variant(parts, 0, "*", "run every minute instead"))
    if current == "*":
        mutations.append(_make_variant(parts, 0, "0", "run once per hour (at :00) instead of every minute"))
        mutations.append(_make_variant(parts, 0, "*/5", "run every 5 minutes instead of every minute"))
        mutations.append(_make_variant(parts, 0, "*/15", "run every 15 minutes instead of every minute"))
    elif current.startswith("*/"):
        mutations.append(_make_variant(parts, 0, "0", "run once per hour instead of on a step"))
    return [m for m in mutations if m is not None]


def _hour_mutations(parts: List[str]) -> List[MutationVariant]:
    current = parts[1]
    mutations = []
    if current != "*":
        mutations.append(_make_variant(parts, 1, "*", "run every hour instead"))
    if current == "*":
        mutations.append(_make_variant(parts, 1, "0", "run once per day at midnight instead of every hour"))
        mutations.append(_make_variant(parts, 1, "*/6", "run every 6 hours instead of every hour"))
    return [m for m in mutations if m is not None]


def _dom_mutations(parts: List[str]) -> List[MutationVariant]:
    current = parts[2]
    mutations = []
    if current != "*":
        mutations.append(_make_variant(parts, 2, "*", "run every day of the month instead"))
    if current == "*":
        mutations.append(_make_variant(parts, 2, "1", "run only on the 1st of the month"))
        mutations.append(_make_variant(parts, 2, "1,15", "run on the 1st and 15th of the month"))
    return [m for m in mutations if m is not None]


def _dow_mutations(parts: List[str]) -> List[MutationVariant]:
    current = parts[4]
    mutations = []
    if current != "*":
        mutations.append(_make_variant(parts, 4, "*", "run on every day of the week instead"))
    if current == "*":
        mutations.append(_make_variant(parts, 4, "1-5", "run on weekdays only (Mon-Fri)"))
        mutations.append(_make_variant(parts, 4, "0,6", "run on weekends only (Sat-Sun)"))
    return [m for m in mutations if m is not None]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def mutate(expression: str, include_invalid: bool = False) -> MutationResult:
    """Generate a set of mutated variants of *expression*.

    Each variant differs from the original by exactly one field, giving the
    caller a quick way to explore neighbouring schedules.

    Args:
        expression: A standard five-field cron expression.
        include_invalid: If True, variants that fail validation are included in
            the result list (marked with ``is_valid=False``).

    Returns:
        A :class:`MutationResult` containing the original expression and all
        generated variants.
    """
    try:
        parsed = parse(expression)
    except ParseError as exc:
        return MutationResult(original=expression, is_valid=False, error=str(exc))

    # Special strings expand to a single token; split into five fields.
    parts = expression.split()
    if len(parts) != 5:
        return MutationResult(
            original=expression,
            is_valid=False,
            error="Mutation requires a standard five-field expression (special strings not supported).",
        )

    variants: List[MutationVariant] = []
    for strategy in (_minute_mutations, _hour_mutations, _dom_mutations, _dow_mutations):
        variants.extend(strategy(parts))

    # Deduplicate by expression string, preserving order
    seen: set = set()
    unique: List[MutationVariant] = []
    for v in variants:
        if v.expression not in seen and v.expression != expression:
            seen.add(v.expression)
            if include_invalid or v.is_valid:
                unique.append(v)

    return MutationResult(original=expression, is_valid=True, variants=unique)
