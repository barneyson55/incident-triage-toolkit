from __future__ import annotations

import json
import re
from pathlib import Path

from .models import LogEvent
from .utils import extract_correlation_id, parse_timestamp

_TS_KEYS = ["timestamp", "time", "ts"]
_LEVEL_KEYS = ["level", "severity", "lvl"]
_COMPONENT_KEYS = ["component", "service", "logger"]
_MESSAGE_KEYS = ["message", "msg", "event"]

_TEXT_TS_RE = re.compile(r"^(?P<ts>\d{4}-\d{2}-\d{2}[T ][0-9:.]{8,}Z?)\s+(?P<rest>.*)$")
_LEVEL_RE = re.compile(r"^(?:\[(?P<bracket>[A-Z]+)\]|(?P<plain>[A-Z]+))\s+(?P<rest>.*)$")
_COMPONENT_RE = re.compile(r"^(?P<component>[A-Za-z0-9_.-]+):\s*(?P<message>.*)$")


def _get_first(data: dict, keys: list[str], default: str | None = None) -> str | None:
    for key in keys:
        if key in data and data[key] not in (None, ""):
            return str(data[key])
    return default


def parse_json_line(line: str) -> LogEvent | None:
    try:
        payload = json.loads(line)
    except json.JSONDecodeError:
        return None
    if not isinstance(payload, dict):
        return None
    ts_value = _get_first(payload, _TS_KEYS)
    if not ts_value:
        return None
    timestamp = parse_timestamp(ts_value)
    if not timestamp:
        return None

    level = (_get_first(payload, _LEVEL_KEYS, "INFO") or "INFO").upper()
    component = _get_first(payload, _COMPONENT_KEYS, "unknown") or "unknown"
    message = _get_first(payload, _MESSAGE_KEYS, "") or ""
    correlation_id = payload.get("correlation_id") or payload.get("cid")
    if correlation_id is None:
        correlation_id = extract_correlation_id(message)

    return LogEvent(
        timestamp=timestamp,
        level=level,
        component=component,
        message=message,
        correlation_id=correlation_id,
        raw=line.rstrip(),
    )


def parse_text_line(line: str) -> LogEvent | None:
    match = _TEXT_TS_RE.match(line)
    if not match:
        return None
    timestamp = parse_timestamp(match.group("ts"))
    if not timestamp:
        return None

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

    return LogEvent(
        timestamp=timestamp,
        level=level,
        component=component,
        message=message,
        correlation_id=correlation_id,
        raw=line.rstrip(),
    )


def parse_line(line: str) -> LogEvent | None:
    stripped = line.lstrip()
    if not stripped:
        return None
    if stripped.startswith("{"):
        parsed = parse_json_line(stripped)
        if parsed:
            return parsed
    return parse_text_line(stripped)


def parse_file(path: str | Path) -> list[LogEvent]:
    path = Path(path)
    events: list[LogEvent] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        event = parse_line(line)
        if event:
            events.append(event)
    return events
