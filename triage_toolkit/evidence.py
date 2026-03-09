from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
import re

from .models import LogEvent

_ERROR_LEVELS = {"ERROR", "CRITICAL", "FATAL"}
_DIGIT_RE = re.compile(r"\d+")
_CORR_RE = re.compile(r"(?:correlation_id|cid)=[A-Za-z0-9-]+", re.IGNORECASE)


@dataclass(frozen=True)
class SignatureEvidence:
    signature: str
    count: int
    first_seen: datetime
    last_seen: datetime
    components: tuple[str, ...]
    representative: LogEvent


def order_events(events: list[LogEvent]) -> list[LogEvent]:
    return sorted(events, key=lambda event: event.timestamp)


def is_error(event: LogEvent) -> bool:
    if event.level.upper() in _ERROR_LEVELS:
        return True
    return "error" in event.message.lower()


def normalize_error_message(message: str) -> str:
    text = message.lower().strip()
    text = _CORR_RE.sub("cid=<id>", text)
    text = _DIGIT_RE.sub("#", text)
    return text


def error_events(events: list[LogEvent]) -> list[LogEvent]:
    return [event for event in order_events(events) if is_error(event)]


def build_signature_evidence(
    events: list[LogEvent],
    *,
    limit: int | None = None,
) -> list[SignatureEvidence]:
    grouped: dict[str, list[LogEvent]] = defaultdict(list)
    for event in error_events(events):
        grouped[normalize_error_message(event.message)].append(event)

    evidence = [
        SignatureEvidence(
            signature=signature,
            count=len(items),
            first_seen=items[0].timestamp,
            last_seen=items[-1].timestamp,
            components=tuple(dict.fromkeys(event.component for event in items)),
            representative=items[0],
        )
        for signature, items in grouped.items()
    ]
    ranked = sorted(
        evidence,
        key=lambda item: (-item.count, item.first_seen, item.signature),
    )
    if limit is not None:
        ranked = ranked[:limit]
    return ranked


def top_error_signatures(events: list[LogEvent], *, limit: int = 3) -> list[dict[str, int | str]]:
    return [
        {"name": item.signature, "count": item.count}
        for item in build_signature_evidence(events, limit=limit)
    ]


def component_counts(events: list[LogEvent], *, limit: int = 5) -> list[tuple[str, int]]:
    counts: Counter[str] = Counter()
    first_seen: dict[str, datetime] = {}
    for event in error_events(events):
        counts[event.component] += 1
        first_seen.setdefault(event.component, event.timestamp)

    ranked = sorted(
        counts.items(),
        key=lambda item: (-item[1], first_seen[item[0]], item[0]),
    )
    return ranked[:limit]


def representative_correlation_ids(events: list[LogEvent], *, limit: int = 5) -> list[str]:
    correlation_ids: list[str] = []
    seen: set[str] = set()
    for event in error_events(events):
        correlation_id = event.correlation_id
        if not correlation_id or correlation_id in seen:
            continue
        correlation_ids.append(correlation_id)
        seen.add(correlation_id)
        if len(correlation_ids) >= limit:
            break
    return correlation_ids
