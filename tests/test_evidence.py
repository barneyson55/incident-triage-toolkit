from __future__ import annotations

from datetime import datetime, timezone

from triage_toolkit.evidence import (
    build_signature_evidence,
    build_source_evidence,
    component_counts,
    evidence_by_source,
    is_error,
    order_events,
    render_error_signature,
    representative_correlation_ids,
    top_error_signatures,
)
from triage_toolkit.models import LogEvent


UTC = timezone.utc


def _ts(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)


def _event(
    timestamp: str,
    *,
    level: str = "INFO",
    component: str = "api",
    message: str = "ok",
    correlation_id: str | None = None,
    source_path: str | None = None,
    line_number: int | None = None,
    source_order: int | None = None,
) -> LogEvent:
    return LogEvent(
        timestamp=_ts(timestamp),
        level=level,
        component=component,
        message=message,
        correlation_id=correlation_id,
        raw=message,
        source_path=source_path,
        line_number=line_number,
        source_order=source_order,
    )


def test_is_error_accepts_error_levels_and_message_hints_only():
    assert is_error(_event("2025-01-01T00:00:01Z", level="ERROR")) is True
    assert is_error(_event("2025-01-01T00:00:01Z", level="critical")) is True
    assert is_error(_event("2025-01-01T00:00:01Z", message="Upstream error on request")) is True
    assert is_error(_event("2025-01-01T00:00:01Z", level="WARN", message="degraded")) is False


def test_order_events_uses_cli_source_order_then_line_number_then_original_position_for_ties():
    tied_timestamp = "2025-01-01T00:00:02Z"
    events = [
        _event(
            tied_timestamp,
            component="fallback-b",
            message="fallback-b",
            source_path="b.log",
            line_number=1,
        ),
        _event(
            tied_timestamp,
            component="source-order-1",
            message="source-order-1",
            source_path="z.log",
            line_number=1,
            source_order=1,
        ),
        _event(
            tied_timestamp,
            component="no-metadata-1",
            message="no-metadata-1",
        ),
        _event(
            tied_timestamp,
            component="source-order-0-line-2",
            message="source-order-0-line-2",
            source_path="a.log",
            line_number=2,
            source_order=0,
        ),
        _event(
            tied_timestamp,
            component="fallback-a",
            message="fallback-a",
            source_path="a.log",
            line_number=1,
        ),
        _event(
            tied_timestamp,
            component="no-metadata-2",
            message="no-metadata-2",
        ),
        _event(
            tied_timestamp,
            component="source-order-0-line-1",
            message="source-order-0-line-1",
            source_path="a.log",
            line_number=1,
            source_order=0,
        ),
    ]

    ordered = order_events(events)

    assert [event.message for event in ordered] == [
        "source-order-0-line-1",
        "source-order-0-line-2",
        "source-order-1",
        "fallback-a",
        "fallback-b",
        "no-metadata-1",
        "no-metadata-2",
    ]


def test_build_signature_evidence_normalizes_ranks_and_uses_earliest_representative_for_ties():
    events = [
        _event(
            "2025-01-01T00:00:05Z",
            level="CRITICAL",
            component="db",
            message="Query failed cid=q-2",
            correlation_id="q-2",
            source_path="db.log",
            line_number=2,
            source_order=2,
        ),
        _event(
            "2025-01-01T00:00:02Z",
            level="ERROR",
            component="api",
            message="Timeout cid=c-9",
            correlation_id="c-9",
            source_path="b.log",
            line_number=1,
            source_order=1,
        ),
        _event(
            "2025-01-01T00:00:01Z",
            level="ERROR",
            component="worker",
            message="Query failed cid=q-1",
            correlation_id="q-1",
            source_path="worker.log",
            line_number=1,
            source_order=0,
        ),
        _event(
            "2025-01-01T00:00:02Z",
            level="ERROR",
            component="worker",
            message="timeout cid=c-2",
            correlation_id="c-2",
            source_path="a.log",
            line_number=1,
            source_order=0,
        ),
        _event(
            "2025-01-01T00:00:04Z",
            component="web",
            message="Upstream error on request 42",
            source_path="web.log",
            line_number=1,
            source_order=3,
        ),
    ]

    evidence = build_signature_evidence(events)

    assert [item.signature for item in evidence] == [
        "query failed cid=<id>",
        "timeout cid=<id>",
        "upstream error on request #",
    ]
    assert [(item.count, item.first_seen.isoformat()) for item in evidence] == [
        (2, "2025-01-01T00:00:01+00:00"),
        (2, "2025-01-01T00:00:02+00:00"),
        (1, "2025-01-01T00:00:04+00:00"),
    ]
    assert evidence[0].components == ("worker", "db")
    assert evidence[1].components == ("worker", "api")
    assert evidence[1].representative.source_path == "a.log"
    assert evidence[1].representative.correlation_id == "c-2"
    assert top_error_signatures(events, limit=2) == [
        {"name": "query failed cid=<id>", "count": 2},
        {"name": "timeout cid=<id>", "count": 2},
    ]


def test_render_error_signature_redacts_sensitive_values_without_changing_digit_normalization():
    message = (
        "Notify Alice@example.com from 10.2.3.4 "
        "cid=550e8400-e29b-41d4-a716-446655440000 "
        "token=AbCdEfGhIjKlMnOpQrSt123456 request 42"
    )

    plain = render_error_signature(message)
    redacted = render_error_signature(message, redact=True)

    assert plain == (
        "notify alice@example.com from #.#.#.# cid=<id> "
        "token=abcdefghijklmnopqrst# request #"
    )
    assert redacted == render_error_signature(message, redact=True)
    assert "alice@example.com" not in redacted
    assert "10.2.3.4" not in redacted
    assert "550e8400-e29b-41d4-a716-446655440000" not in redacted
    assert "AbCdEfGhIjKlMnOpQrSt123456" not in redacted
    assert "request #" in redacted
    assert "[redacted-email:" in redacted
    assert "[redacted-ip:" in redacted
    assert "[redacted-id:" in redacted
    assert "[redacted-secret:" in redacted


def test_build_source_evidence_ranks_by_count_then_first_seen_then_source_label():
    events = [
        _event(
            "2025-01-01T00:00:03Z",
            level="ERROR",
            component="api",
            message="failed-a-2",
            source_path="a.log",
            line_number=2,
            source_order=0,
        ),
        _event(
            "2025-01-01T00:00:02Z",
            level="ERROR",
            component="worker",
            message="failed-c",
            source_path="c.log",
            line_number=1,
            source_order=2,
        ),
        _event(
            "2025-01-01T00:00:01Z",
            level="ERROR",
            component="api",
            message="failed-a-1",
            source_path="a.log",
            line_number=1,
            source_order=0,
        ),
        _event(
            "2025-01-01T00:00:02Z",
            level="ERROR",
            component="db",
            message="failed-b",
            source_path="b.log",
            line_number=1,
            source_order=1,
        ),
    ]

    ranked = build_source_evidence(events)

    assert [(item.source, item.count, item.first_seen.isoformat()) for item in ranked] == [
        ("a.log", 2, "2025-01-01T00:00:01+00:00"),
        ("b.log", 1, "2025-01-01T00:00:02+00:00"),
        ("c.log", 1, "2025-01-01T00:00:02+00:00"),
    ]
    assert evidence_by_source(events, limit=2) == [
        {"source": "a.log", "count": 2},
        {"source": "b.log", "count": 1},
    ]


def test_component_counts_use_error_events_and_rank_by_count_first_seen_then_name():
    events = [
        _event("2025-01-01T00:00:03Z", level="ERROR", component="api", message="timeout"),
        _event("2025-01-01T00:00:01Z", level="ERROR", component="worker", message="failed"),
        _event("2025-01-01T00:00:02Z", level="ERROR", component="api", message="timeout"),
        _event("2025-01-01T00:00:01Z", level="ERROR", component="db", message="failed"),
        _event("2025-01-01T00:00:04Z", component="web", message="accepted"),
    ]

    assert component_counts(events, limit=3) == [("api", 2), ("db", 1), ("worker", 1)]


def test_representative_correlation_ids_return_first_unique_ids_from_ordered_error_events():
    events = [
        _event(
            "2025-01-01T00:00:02Z",
            level="ERROR",
            component="api",
            message="timeout cid=c-2",
            correlation_id="c-2",
            source_order=1,
        ),
        _event(
            "2025-01-01T00:00:01Z",
            component="web",
            message="upstream error on request",
            correlation_id="c-3",
            source_order=2,
        ),
        _event(
            "2025-01-01T00:00:02Z",
            level="ERROR",
            component="worker",
            message="timeout cid=c-1",
            correlation_id="c-1",
            source_order=0,
        ),
        _event(
            "2025-01-01T00:00:03Z",
            level="ERROR",
            component="db",
            message="timeout cid=c-1",
            correlation_id="c-1",
            source_order=3,
        ),
        _event(
            "2025-01-01T00:00:04Z",
            level="WARN",
            component="cache",
            message="degraded",
            correlation_id="skip-me",
            source_order=4,
        ),
        _event(
            "2025-01-01T00:00:05Z",
            level="ERROR",
            component="queue",
            message="failed without id",
            correlation_id=None,
            source_order=5,
        ),
    ]

    assert representative_correlation_ids(events, limit=3) == ["c-3", "c-1", "c-2"]
