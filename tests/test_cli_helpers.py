from __future__ import annotations

import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import pytest

import triage_toolkit.cli as cli_module
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


def _summary(
    *,
    total_lines: int,
    parsed_lines: int,
    dropped_reasons: dict[str, int] | None = None,
    dropped_line_diagnostics: list[dict[str, object]] | None = None,
) -> dict[str, object]:
    dropped_lines = total_lines - parsed_lines
    summary: dict[str, object] = {
        "total_lines": total_lines,
        "parsed_lines": parsed_lines,
        "dropped_lines": dropped_lines,
        "drop_ratio": round(dropped_lines / total_lines, 6) if total_lines else 0.0,
        "dropped_reasons": dropped_reasons or {},
    }
    if dropped_line_diagnostics is not None:
        summary["dropped_line_diagnostics"] = dropped_line_diagnostics
    return summary


def test_merge_parse_summaries_aggregates_reason_counts_and_rounds_drop_ratio():
    merged = cli_module._merge_parse_summaries(
        [
            _summary(total_lines=3, parsed_lines=2, dropped_reasons={"unrecognized_text": 1}),
            _summary(total_lines=4, parsed_lines=3, dropped_reasons={"invalid_timestamp": 1}),
        ]
    )

    assert merged == {
        "total_lines": 7,
        "parsed_lines": 5,
        "dropped_lines": 2,
        "drop_ratio": 0.285714,
        "dropped_reasons": {
            "invalid_timestamp": 1,
            "unrecognized_text": 1,
        },
    }


def test_apply_event_filters_uses_or_within_each_flag_family_and_and_across_families():
    events = [
        _event("2025-01-01T00:00:01Z", component="api", message="accepted", correlation_id="c-1"),
        _event(
            "2025-01-01T00:00:02Z",
            level="ERROR",
            component="api",
            message="timeout-api",
            correlation_id="c-2",
        ),
        _event(
            "2025-01-01T00:00:03Z",
            level="ERROR",
            component="worker",
            message="timeout-worker",
            correlation_id="c-2",
        ),
        _event(
            "2025-01-01T00:00:04Z",
            level="ERROR",
            component="web",
            message="timeout-web",
            correlation_id="c-3",
        ),
    ]

    filtered = cli_module._apply_event_filters(
        events,
        components=["api", "worker"],
        levels=["error"],
        correlation_ids=["c-2"],
    )

    assert [event.message for event in filtered] == ["timeout-api", "timeout-worker"]


def test_strict_parse_error_prioritizes_zero_parsed_lines_and_formats_drop_ratio_thresholds():
    empty_error = cli_module._strict_parse_error(
        _summary(total_lines=2, parsed_lines=0, dropped_reasons={"unrecognized_text": 2}),
        1.0,
    )

    ratio_error = cli_module._strict_parse_error(
        _summary(total_lines=3, parsed_lines=2, dropped_reasons={"unrecognized_text": 1}),
        0.3,
    )

    assert empty_error is not None
    assert empty_error.startswith("Strict parse gate failed: parsed_lines == 0")
    assert (
        ratio_error
        == "Strict parse gate failed: drop_ratio=0.333333 exceeds max_drop_ratio=0.300000 "
        "(summary={\"drop_ratio\": 0.333333, \"dropped_lines\": 1, \"dropped_reasons\": {\"unrecognized_text\": 1}, \"parsed_lines\": 2, \"total_lines\": 3})"
    )
    assert (
        cli_module._strict_parse_error(
            _summary(total_lines=3, parsed_lines=2, dropped_reasons={"unrecognized_text": 1}),
            1 / 3,
        )
        is None
    )


def test_top_items_orders_by_count_then_name_and_applies_limit():
    ranked = cli_module._top_items(Counter({"worker": 1, "db": 2, "api": 2, "cache": 1}), limit=3)

    assert ranked == [
        {"name": "api", "count": 2},
        {"name": "db", "count": 2},
        {"name": "cache", "count": 1},
    ]


def test_build_incident_summary_includes_ranked_automation_fields_for_mixed_event_sets():
    events = [
        _event(
            "2025-01-01T00:00:01Z",
            component="web",
            message="accepted",
            correlation_id="c-web",
            source_path="web.log",
            line_number=1,
            source_order=0,
        ),
        _event(
            "2025-01-01T00:00:02Z",
            level="ERROR",
            component="api",
            message="Timeout cid=c-1",
            correlation_id="c-1",
            source_path="a.log",
            line_number=1,
            source_order=1,
        ),
        _event(
            "2025-01-01T00:00:02Z",
            level="ERROR",
            component="worker",
            message="Timeout cid=c-2",
            correlation_id="c-2",
            source_path="b.log",
            line_number=1,
            source_order=2,
        ),
        _event(
            "2025-01-01T00:00:03Z",
            level="WARN",
            component="cache",
            message="error path engaged",
            source_path="c.log",
            line_number=1,
            source_order=3,
        ),
        _event(
            "2025-01-01T00:00:04Z",
            component="web",
            message="healthy",
            source_path="web.log",
            line_number=2,
            source_order=0,
        ),
        _event(
            "2025-01-01T00:00:05Z",
            level="CRITICAL",
            component="db",
            message="Query failed cid=q-1",
            correlation_id="q-1",
            source_path="d.log",
            line_number=1,
            source_order=4,
        ),
    ]

    assert cli_module._build_incident_summary(events) == {
        "schema_version": cli_module.SUMMARY_SCHEMA_VERSION,
        "incident_window": {
            "start": "2025-01-01T00:00:01+00:00",
            "end": "2025-01-01T00:00:05+00:00",
        },
        "event_count": 6,
        "error_count": 4,
        "top_components": [
            {"name": "web", "count": 2},
            {"name": "api", "count": 1},
            {"name": "cache", "count": 1},
        ],
        "top_error_signatures": [
            {"name": "timeout cid=<id>", "count": 2},
            {"name": "error path engaged", "count": 1},
            {"name": "query failed cid=<id>", "count": 1},
        ],
        "evidence_by_source": [
            {"source": "a.log", "count": 1},
            {"source": "b.log", "count": 1},
            {"source": "c.log", "count": 1},
            {"source": "d.log", "count": 1},
        ],
        "correlation_id_coverage": {
            "covered_events": 4,
            "total_events": 6,
            "coverage_ratio": 0.666667,
        },
    }


def test_redact_parse_summary_reuses_deterministic_placeholders_across_diagnostics():
    repeated_secret = "AbCdEfGhIjKlMnOpQrSt123456"
    repeated_id = "550e8400-e29b-41d4-a716-446655440000"
    summary = _summary(
        total_lines=3,
        parsed_lines=1,
        dropped_reasons={"unrecognized_text": 2},
        dropped_line_diagnostics=[
            {
                "source_path": "a.log",
                "line_number": 2,
                "reason": "unrecognized_text",
                "raw_line": (
                    f"notify alice@example.com from 10.2.3.4 cid={repeated_id} token={repeated_secret}"
                ),
            },
            {
                "source_path": "b.log",
                "line_number": 4,
                "reason": "unrecognized_text",
                "raw_line": (
                    f"repeat alice@example.com via 10.2.3.4 cid={repeated_id} token={repeated_secret}"
                ),
            },
        ],
    )

    redacted = cli_module._redact_parse_summary(summary)
    first_placeholders = re.findall(r"\[redacted-[^\]]+\]", redacted["dropped_line_diagnostics"][0]["raw_line"])
    second_placeholders = re.findall(r"\[redacted-[^\]]+\]", redacted["dropped_line_diagnostics"][1]["raw_line"])

    assert redacted["total_lines"] == 3
    assert first_placeholders == second_placeholders
    assert len(first_placeholders) == 4
    assert "alice@example.com" not in redacted["dropped_line_diagnostics"][0]["raw_line"]
    assert "10.2.3.4" not in redacted["dropped_line_diagnostics"][0]["raw_line"]
    assert repeated_id not in redacted["dropped_line_diagnostics"][0]["raw_line"]
    assert repeated_secret not in redacted["dropped_line_diagnostics"][0]["raw_line"]


def test_redact_parse_summary_is_unchanged_when_diagnostics_are_absent():
    summary = _summary(total_lines=2, parsed_lines=2)

    assert cli_module._redact_parse_summary(summary) == summary


def test_read_events_for_parse_merges_summaries_orders_events_and_carries_forward_diagnostics(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    source_a = tmp_path / "a.log"
    source_b = tmp_path / "b.log"
    call_history: list[tuple[str, int | None, int]] = []

    def fake_read_events_with_summary(
        path: Path,
        *,
        source_order: int | None = None,
        diagnostics_limit: int = 0,
    ) -> tuple[list[LogEvent], dict[str, object]]:
        call_history.append((str(path), source_order, diagnostics_limit))

        if path == source_a:
            diagnostics = (
                [
                    {
                        "source_path": str(path),
                        "line_number": 2,
                        "reason": "unrecognized_text",
                        "raw_line": "bad-a",
                    }
                ]
                if diagnostics_limit > 0
                else []
            )
            return (
                [
                    _event(
                        "2025-01-01T00:00:02Z",
                        component="api",
                        message="from-a",
                        source_path=str(path),
                        line_number=1,
                        source_order=source_order,
                    )
                ],
                _summary(
                    total_lines=2,
                    parsed_lines=1,
                    dropped_reasons={"unrecognized_text": 1},
                    dropped_line_diagnostics=diagnostics if diagnostics_limit > 0 else None,
                ),
            )

        assert path == source_b
        diagnostics = (
            [
                {
                    "source_path": str(path),
                    "line_number": 2,
                    "reason": "invalid_timestamp",
                    "raw_line": "bad-b",
                }
            ]
            if diagnostics_limit > 0
            else []
        )
        return (
            [
                _event(
                    "2025-01-01T00:00:03Z",
                    component="db",
                    message="from-b",
                    source_path=str(path),
                    line_number=1,
                    source_order=source_order,
                )
            ],
            _summary(
                total_lines=2,
                parsed_lines=1,
                dropped_reasons={"invalid_timestamp": 1},
                dropped_line_diagnostics=diagnostics if diagnostics_limit > 0 else None,
            ),
        )

    def fake_read_events_from_stdin(
        *,
        source_order: int | None = None,
        diagnostics_limit: int = 0,
    ) -> tuple[list[LogEvent], dict[str, object]]:
        call_history.append(("-", source_order, diagnostics_limit))
        diagnostics = [
            {
                "source_path": "-",
                "line_number": 2,
                "reason": "unrecognized_text",
                "raw_line": "bad-stdin-1",
            },
            {
                "source_path": "-",
                "line_number": 3,
                "reason": "unrecognized_text",
                "raw_line": "bad-stdin-2",
            },
        ][:diagnostics_limit]
        return (
            [
                _event(
                    "2025-01-01T00:00:01Z",
                    component="worker",
                    message="from-stdin",
                    source_path="-",
                    line_number=1,
                    source_order=source_order,
                )
            ],
            _summary(
                total_lines=3,
                parsed_lines=1,
                dropped_reasons={"unrecognized_text": 2},
                dropped_line_diagnostics=diagnostics if diagnostics_limit > 0 else None,
            ),
        )

    monkeypatch.setattr(cli_module, "_read_events_with_summary", fake_read_events_with_summary)
    monkeypatch.setattr(cli_module, "_read_events_from_stdin", fake_read_events_from_stdin)

    events, summary = cli_module._read_events_for_parse(
        [source_a, Path("-"), source_b],
        diagnostics_limit=2,
    )

    assert call_history == [
        (str(source_a), 0, 2),
        ("-", 1, 1),
        (str(source_b), 2, 0),
    ]
    assert [event.message for event in events] == ["from-stdin", "from-a", "from-b"]
    assert summary == {
        "total_lines": 7,
        "parsed_lines": 3,
        "dropped_lines": 4,
        "drop_ratio": 0.571429,
        "dropped_reasons": {
            "invalid_timestamp": 1,
            "unrecognized_text": 3,
        },
        "dropped_line_diagnostics": [
            {
                "source_path": str(source_a),
                "line_number": 2,
                "reason": "unrecognized_text",
                "raw_line": "bad-a",
            },
            {
                "source_path": "-",
                "line_number": 2,
                "reason": "unrecognized_text",
                "raw_line": "bad-stdin-1",
            },
        ],
        "per_source": [
            {
                "path": str(source_a),
                "total_lines": 2,
                "parsed_lines": 1,
                "dropped_lines": 1,
                "drop_ratio": 0.5,
                "dropped_reasons": {"unrecognized_text": 1},
            },
            {
                "path": "-",
                "total_lines": 3,
                "parsed_lines": 1,
                "dropped_lines": 2,
                "drop_ratio": 0.666667,
                "dropped_reasons": {"unrecognized_text": 2},
            },
            {
                "path": str(source_b),
                "total_lines": 2,
                "parsed_lines": 1,
                "dropped_lines": 1,
                "drop_ratio": 0.5,
                "dropped_reasons": {"invalid_timestamp": 1},
            },
        ],
    }



def test_read_events_for_parse_rejects_duplicate_stdin_sources(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        cli_module,
        "_fail",
        lambda message: (_ for _ in ()).throw(RuntimeError(message)),
    )

    with pytest.raises(RuntimeError, match="Standard input source '-' may be specified at most once."):
        cli_module._read_events_for_parse([Path("-"), Path("-")])



def test_write_output_writes_to_stdout_without_extra_newline(capsys: pytest.CaptureFixture[str]):
    cli_module._write_output("-", "hello")

    captured = capsys.readouterr()
    assert captured.out == "hello"
    assert captured.err == ""



def test_write_output_creates_parent_directories_before_writing(tmp_path: Path):
    output = tmp_path / "nested" / "outputs" / "result.json"

    cli_module._write_output(str(output), '{"ok": true}')

    assert output.read_text(encoding="utf-8") == '{"ok": true}'
