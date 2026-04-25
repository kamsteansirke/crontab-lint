"""Formatter for expression aliases."""
from __future__ import annotations

from typing import List, Optional
from .expression_aliases import Alias, AliasStore


def format_alias(alias: Alias, index: Optional[int] = None) -> str:
    """Format a single alias into a human-readable string.

    Args:
        alias: The alias to format.
        index: Optional 1-based index to prefix the output with.

    Returns:
        A formatted string representation of the alias.
    """
    prefix = f"{index}. " if index is not None else ""
    lines = [
        f"{prefix}[{alias.name}]  {alias.expression}",
    ]
    if alias.description:
        lines.append(f"   Description : {alias.description}")
    return "\n".join(lines)


def format_aliases(aliases: List[Alias]) -> str:
    """Format a list of aliases into a numbered, human-readable string.

    Args:
        aliases: The list of aliases to format.

    Returns:
        A formatted string with each alias separated by a blank line,
        or a message indicating no aliases were found.
    """
    if not aliases:
        return "No aliases found."
    parts = [format_alias(a, i + 1) for i, a in enumerate(aliases)]
    return "\n\n".join(parts)


def format_summary(store: AliasStore) -> str:
    """Format a short summary of the alias store.

    Args:
        store: The alias store to summarise.

    Returns:
        A one-line summary string with the total alias count.
    """
    total = len(store.all())
    return f"Alias store: {total} alias{'es' if total != 1 else ''} defined."
