"""Formatter for snapshot comparison output."""
from crontab_lint.snapshot import Snapshot


def format_snapshot(snapshot: Snapshot) -> str:
    lines = [f"Snapshot: {snapshot.name}"]
    if snapshot.created_at:
        lines.append(f"  Created: {snapshot.created_at}")
    lines.append(f"  Expressions ({len(snapshot.expressions)}):")
    for expr in snapshot.expressions:
        lines.append(f"    {expr}")
    return "\n".join(lines)


def format_comparison(diff: dict, old_name: str, new_name: str) -> str:
    lines = [f"Comparing '{old_name}' -> '{new_name}'"]
    if diff["added"]:
        lines.append("  Added:")
        for e in diff["added"]:
            lines.append(f"    + {e}")
    if diff["removed"]:
        lines.append("  Removed:")
        for e in diff["removed"]:
            lines.append(f"    - {e}")
    if diff["unchanged"]:
        lines.append(f"  Unchanged: {len(diff['unchanged'])} expression(s)")
    if not diff["added"] and not diff["removed"]:
        lines.append("  No changes detected.")
    return "\n".join(lines)


def format_list(names: list) -> str:
    if not names:
        return "No snapshots stored."
    return "Snapshots:\n" + "\n".join(f"  - {n}" for n in names)
