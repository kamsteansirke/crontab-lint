"""Check crontab expressions for timezone-related issues and annotate with UTC offset info."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime, timezone, timedelta
import zoneinfo

from .parser import parse, ParseError


@dataclass
class TimezoneWarning:
    code: str
    message: str


@dataclass
class TimezoneCheckResult:
    expression: str
    tz_name: str
    utc_offset: Optional[str]
    is_valid_tz: bool
    warnings: List[TimezoneWarning] = field(default_factory=list)

    @property
    def has_warnings(self) -> bool:
        return bool(self.warnings)


def _get_utc_offset(tz_name: str) -> Optional[str]:
    try:
        tz = zoneinfo.ZoneInfo(tz_name)
        now = datetime.now(tz)
        offset = now.utcoffset()
        if offset is None:
            return None
        total_seconds = int(offset.total_seconds())
        sign = "+" if total_seconds >= 0 else "-"
        abs_seconds = abs(total_seconds)
        hours, remainder = divmod(abs_seconds, 3600)
        minutes = remainder // 60
        return f"UTC{sign}{hours:02d}:{minutes:02d}"
    except (zoneinfo.ZoneInfoNotFoundError, KeyError):
        return None


def _build_warnings(expression: str, tz_name: str) -> List[TimezoneWarning]:
    warnings: List[TimezoneWarning] = []
    try:
        tz = zoneinfo.ZoneInfo(tz_name)
        now = datetime.now(tz)
        offset = now.utcoffset()
        if offset is not None and offset == timedelta(0) and tz_name not in ("UTC", "Etc/UTC"):
            warnings.append(TimezoneWarning(
                code="UTC_ALIAS",
                message=f"Timezone '{tz_name}' currently has UTC+00:00 offset but is not canonical UTC."
            ))
    except (zoneinfo.ZoneInfoNotFoundError, KeyError):
        pass

    try:
        result = parse(expression)
        if hasattr(result, 'minute') and result.minute == "*" and hasattr(result, 'hour') and result.hour == "*":
            warnings.append(TimezoneWarning(
                code="HIGH_FREQUENCY",
                message="Expression runs every minute; timezone offset has minimal impact."
            ))
    except ParseError:
        pass

    return warnings


def check(expression: str, tz_name: str) -> TimezoneCheckResult:
    """Check a cron expression in the context of a given timezone."""
    utc_offset = _get_utc_offset(tz_name)
    is_valid_tz = utc_offset is not None
    warnings = _build_warnings(expression, tz_name) if is_valid_tz else [
        TimezoneWarning(code="UNKNOWN_TZ", message=f"Unknown timezone: '{tz_name}'.")
    ]
    return TimezoneCheckResult(
        expression=expression,
        tz_name=tz_name,
        utc_offset=utc_offset,
        is_valid_tz=is_valid_tz,
        warnings=warnings,
    )
