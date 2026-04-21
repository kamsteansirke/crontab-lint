"""Formatting helpers for Profile objects."""
from __future__ import annotations

from typing import List, Optional
from crontab_lint.profile import Profile


def format_profile(profile: Profile, index: Optional[int] = None) -> str:
    prefix = f"{index}. " if index is not None else ""
    lines = [f"{prefix}[{profile.name}]"]
    if profile.description:
        lines.append(f"  Description : {profile.description}")
    if profile.tags:
        lines.append(f"  Tags        : {', '.join(profile.tags)}")
    if profile.expressions:
        lines.append(f"  Expressions ({len(profile.expressions)}):")
        for expr in profile.expressions:
            lines.append(f"    - {expr}")
    else:
        lines.append("  Expressions : (none)")
    return "\n".join(lines)


def format_profiles(profiles: List[Profile]) -> str:
    if not profiles:
        return "No profiles found."
    return "\n\n".join(format_profile(p, i + 1) for i, p in enumerate(profiles))


def format_summary(profiles: List[Profile]) -> str:
    total = len(profiles)
    total_exprs = sum(len(p.expressions) for p in profiles)
    return f"{total} profile(s), {total_exprs} expression(s) total."
