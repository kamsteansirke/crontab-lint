"""Parser for crontab expressions."""

import re
from dataclasses import dataclass
from typing import Optional

FIELD_NAMES = ["minute", "hour", "day_of_month", "month", "day_of_week"]
FIELD_RANGES = {
    "minute": (0, 59),
    "hour": (0, 23),
    "day_of_month": (1, 31),
    "month": (1, 12),
    "day_of_week": (0, 7),
}

SPECIAL_STRINGS = {
    "@yearly": "0 0 1 1 *",
    "@annually": "0 0 1 1 *",
    "@monthly": "0 0 1 * *",
    "@weekly": "0 0 * * 0",
    "@daily": "0 0 * * *",
    "@midnight": "0 0 * * *",
    "@hourly": "0 * * * *",
}


@dataclass
class CronField:
    name: str
    raw: str
    min_val: int
    max_val: int


@dataclass
class CronExpression:
    raw: str
    fields: list[CronField]
    command: Optional[str] = None


class ParseError(ValueError):
    pass


def parse(expression: str) -> CronExpression:
    """Parse a crontab expression string into a CronExpression."""
    expression = expression.strip()

    if expression in SPECIAL_STRINGS:
        expression = SPECIAL_STRINGS[expression]

    parts = expression.split()
    if len(parts) < 5:
        raise ParseError(
            f"Expected at least 5 fields, got {len(parts)}: '{expression}'"
        )

    command = " ".join(parts[5:]) if len(parts) > 5 else None
    field_parts = parts[:5]

    fields = []
    for name, raw in zip(FIELD_NAMES, field_parts):
        min_val, max_val = FIELD_RANGES[name]
        fields.append(CronField(name=name, raw=raw, min_val=min_val, max_val=max_val))

    return CronExpression(raw=expression, fields=fields, command=command)


def validate_field(field: CronField) -> list[str]:
    """Validate a single cron field and return a list of error messages."""
    errors = []
    raw = field.raw

    if raw == "*":
        return errors

    segments = raw.split(",")
    for segment in segments:
        if "/" in segment:
            parts = segment.split("/", 1)
            base, step = parts
            if not step.isdigit() or int(step) == 0:
                errors.append(f"[{field.name}] Invalid step value in '{segment}'")
            if base != "*" and "-" not in base and not base.isdigit():
                errors.append(f"[{field.name}] Invalid base in step expression '{segment}'")
        elif "-" in segment:
            parts = segment.split("-", 1)
            if not (parts[0].isdigit() and parts[1].isdigit()):
                errors.append(f"[{field.name}] Invalid range '{segment}'")
            else:
                lo, hi = int(parts[0]), int(parts[1])
                if lo > hi:
                    errors.append(f"[{field.name}] Range start {lo} > end {hi}")
                if lo < field.min_val or hi > field.max_val:
                    errors.append(
                        f"[{field.name}] Range {lo}-{hi} out of bounds "
                        f"({field.min_val}-{field.max_val})"
                    )
        elif segment.isdigit():
            val = int(segment)
            if val < field.min_val or val > field.max_val:
                errors.append(
                    f"[{field.name}] Value {val} out of bounds "
                    f"({field.min_val}-{field.max_val})"
                )
        else:
            errors.append(f"[{field.name}] Unrecognized token '{segment}'")

    return errors
