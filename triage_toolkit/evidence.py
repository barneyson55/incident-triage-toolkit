from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
import re

from .models import LogEvent
from .redaction import redact_text

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


@dataclass(frozen=True)
class SourceEvidence:
    source: str
    count: int
    first_seen: datetime


def _source_tie_break_key(event: LogEvent) -> tuple[int, int | str]:
    if event.source_order is not None:
        return (0, event.source_order)
    if event.source_path is not None:
        return (1, event.source_path)
    return (2, "")


def order_events(events: list[LogEvent]) -> list[LogEvent]:
    """Sort by canonical UTC timestamp, then source tie-break metadata, then line order."""
    return [
        event
        for _, event in sorted(
            enumerate(events),
            key=lambda item: (
                item[1].timestamp,
                *_source_tie_break_key(item[1]),
                0 if item[1].line_number is not None else 1,
                item[1].line_number if item[1].line_number is not None else 0,
                item[0],
            ),
        )
    ]


def is_error(event: LogEvent) -> bool:
    if event.level.upper() in _ERROR_LEVELS:
        return True
    return "error" in event.message.lower()


def normalize_error_message(message: str) -> str:
    return render_error_signature(message)


def render_error_signature(message: str, *, redact: bool = False) -> str:
    text = message.lower().strip()
    if redact:
        text = redact_text(text)
    else:
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


def _source_label(event: LogEvent) -> str:
    return event.source_path or "n/a"


def build_source_evidence(
    events: list[LogEvent],
    *,
    limit: int | None = None,
) -> list[SourceEvidence]:
    grouped: dict[str, list[LogEvent]] = defaultdict(list)
    for event in error_events(events):
        grouped[_source_label(event)].append(event)

    evidence = [
        SourceEvidence(
            source=source,
            count=len(items),
            first_seen=items[0].timestamp,
        )
        for source, items in grouped.items()
    ]
    ranked = sorted(
        evidence,
        key=lambda item: (-item.count, item.first_seen, item.source),
    )
    if limit is not None:
        ranked = ranked[:limit]
    return ranked


def evidence_by_source(events: list[LogEvent], *, limit: int | None = None) -> list[dict[str, int | str]]:
    return [
        {"source": item.source, "count": item.count}
        for item in build_source_evidence(events, limit=limit)
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
