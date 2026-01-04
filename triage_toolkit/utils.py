from __future__ import annotations

from datetime import datetime, timezone
import re

_CORR_RE = re.compile(r"(?:correlation_id|cid)=([A-Za-z0-9-]+)")

_TS_FORMATS = [
    "%Y-%m-%dT%H:%M:%SZ",
    "%Y-%m-%dT%H:%M:%S.%fZ",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%d %H:%M:%S.%f",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%dT%H:%M:%S.%f",
]


def parse_timestamp(value: str) -> datetime | None:
    value = value.strip()
    if not value:
        return None
    if value.endswith("Z") and "+" not in value:
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            pass
    for fmt in _TS_FORMATS:
        try:
            dt = datetime.strptime(value, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except ValueError:
            continue
    try:
        dt = datetime.fromisoformat(value)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def extract_correlation_id(message: str) -> str | None:
    match = _CORR_RE.search(message or "")
    if not match:
        return None
    return match.group(1)
