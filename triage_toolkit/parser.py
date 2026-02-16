from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

from .models import LogEvent
from .utils import extract_correlation_id, parse_timestamp

_TS_KEYS = ["timestamp", "time", "ts"]
_LEVEL_KEYS = ["level", "severity", "lvl"]
_COMPONENT_KEYS = ["component", "service", "logger"]
_MESSAGE_KEYS = ["message", "msg", "event"]

_TEXT_TS_RE = re.compile(r"^(?P<ts>\d{4}-\d{2}-\d{2}[T ][0-9:.]{8,}Z?)\s+(?P<rest>.*)$")
_LEVEL_RE = re.compile(r"^(?:\[(?P<bracket>[A-Z]+)\]|(?P<plain>[A-Z]+))\s+(?P<rest>.*)$")
_COMPONENT_RE = re.compile(r"^(?P<component>[A-Za-z0-9_.-]+):\s*(?P<message>.*)$")

_DROP_BLANK_LINE = "blank_line"
_DROP_INVALID_JSON = "invalid_json"
_DROP_JSON_NOT_OBJECT = "json_not_object"
_DROP_MISSING_TIMESTAMP = "missing_timestamp"
_DROP_INVALID_TIMESTAMP = "invalid_timestamp"
_DROP_UNRECOGNIZED_TEXT = "unrecognized_text"
_DROP_UNKNOWN = "unknown"


def _get_first(data: dict, keys: list[str], default: str | None = None) -> str | None:
    for key in keys:
        if key in data and data[key] not in (None, ""):
            return str(data[key])
    return default


def _parse_json_line_with_reason(line: str) -> tuple[LogEvent | None, str | None]:
    try:
        payload = json.loads(line)
    except json.JSONDecodeError:
        return None, _DROP_INVALID_JSON
    if not isinstance(payload, dict):
        return None, _DROP_JSON_NOT_OBJECT

    ts_value = _get_first(payload, _TS_KEYS)
    if not ts_value:
        return None, _DROP_MISSING_TIMESTAMP
    timestamp = parse_timestamp(ts_value)
    if not timestamp:
        return None, _DROP_INVALID_TIMESTAMP

    level = (_get_first(payload, _LEVEL_KEYS, "INFO") or "INFO").upper()
    component = _get_first(payload, _COMPONENT_KEYS, "unknown") or "unknown"
    message = _get_first(payload, _MESSAGE_KEYS, "") or ""
    correlation_id = payload.get("correlation_id") or payload.get("cid")
    if correlation_id is None:
        correlation_id = extract_correlation_id(message)

    return (
        LogEvent(
            timestamp=timestamp,
            level=level,
            component=component,
            message=message,
            correlation_id=correlation_id,
            raw=line.rstrip(),
        ),
        None,
    )


def parse_json_line(line: str) -> LogEvent | None:
    event, _ = _parse_json_line_with_reason(line)
    return event


def _parse_text_line_with_reason(line: str) -> tuple[LogEvent | None, str | None]:
    match = _TEXT_TS_RE.match(line)
    if not match:
        return None, _DROP_UNRECOGNIZED_TEXT

    timestamp = parse_timestamp(match.group("ts"))
    if not timestamp:
        return None, _DROP_INVALID_TIMESTAMP

    rest = match.group("rest").strip()
    level = "INFO"
    level_match = _LEVEL_RE.match(rest)
    if level_match:
        level = (level_match.group("bracket") or level_match.group("plain") or "INFO").upper()
        rest = level_match.group("rest").strip()

    component = "unknown"
    message = rest
    comp_match = _COMPONENT_RE.match(rest)
    if comp_match:
        component = comp_match.group("component")
        message = comp_match.group("message").strip()

    correlation_id = extract_correlation_id(message)

    return (
        LogEvent(
            timestamp=timestamp,
            level=level,
            component=component,
            message=message,
            correlation_id=correlation_id,
            raw=line.rstrip(),
        ),
        None,
    )


def parse_text_line(line: str) -> LogEvent | None:
    event, _ = _parse_text_line_with_reason(line)
    return event


def parse_line_with_reason(line: str) -> tuple[LogEvent | None, str | None]:
    stripped = line.lstrip()
    if not stripped:
        return None, _DROP_BLANK_LINE

    if stripped.startswith("{"):
        event, drop_reason = _parse_json_line_with_reason(stripped)
    else:
        event, drop_reason = _parse_text_line_with_reason(stripped)

    if event:
        return event, None
    return None, drop_reason or _DROP_UNKNOWN


def parse_line(line: str) -> LogEvent | None:
    event, _ = parse_line_with_reason(line)
    return event


def _build_parse_summary(
    *,
    total_lines: int,
    parsed_lines: int,
    dropped_reasons: Counter[str],
) -> dict[str, Any]:
    dropped_lines = total_lines - parsed_lines
    drop_ratio = dropped_lines / total_lines if total_lines else 0.0
    summary = {
        "total_lines": total_lines,
        "parsed_lines": parsed_lines,
        "dropped_lines": dropped_lines,
        "drop_ratio": round(drop_ratio, 6),
        "dropped_reasons": {
            reason: dropped_reasons[reason] for reason in sorted(dropped_reasons)
        },
    }
    return summary


def parse_lines_with_summary(lines: Iterable[str]) -> tuple[list[LogEvent], dict[str, Any]]:
    events: list[LogEvent] = []
    dropped_reasons: Counter[str] = Counter()
    total_lines = 0

    for line in lines:
        total_lines += 1
        event, drop_reason = parse_line_with_reason(line)
        if event:
            events.append(event)
        else:
            dropped_reasons[drop_reason or _DROP_UNKNOWN] += 1

    summary = _build_parse_summary(
        total_lines=total_lines,
        parsed_lines=len(events),
        dropped_reasons=dropped_reasons,
    )
    return events, summary


def parse_file_with_summary(path: str | Path) -> tuple[list[LogEvent], dict[str, Any]]:
    path = Path(path)
    return parse_lines_with_summary(path.read_text(encoding="utf-8").splitlines())


def parse_file(path: str | Path) -> list[LogEvent]:
    events, _ = parse_file_with_summary(path)
    return events
