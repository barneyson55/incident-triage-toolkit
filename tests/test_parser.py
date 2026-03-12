import json
from collections import Counter
from pathlib import Path

import pytest

import triage_toolkit.parser as parser_module
from triage_toolkit.parser import (
    parse_file_with_summary,
    parse_json_line,
    parse_line,
    parse_line_with_reason,
    parse_lines_with_summary,
    parse_text_line,
)


def test_source_timestamp_provenance_extracts_trimmed_offset_variants():
    assert parser_module._source_timestamp_provenance(" 2025-01-01T00:00:02Z ") == (
        "2025-01-01T00:00:02Z",
        "Z",
    )
    assert parser_module._source_timestamp_provenance("2025-01-01T02:00:02+02:00") == (
        "2025-01-01T02:00:02+02:00",
        "+02:00",
    )
    assert parser_module._source_timestamp_provenance("2025-01-01 00:00:02") == (
        "2025-01-01 00:00:02",
        None,
    )



def test_build_parse_summary_sorts_reasons_rounds_ratio_and_preserves_optional_diagnostics():
    summary = parser_module._build_parse_summary(
        total_lines=3,
        parsed_lines=1,
        dropped_reasons=Counter({"unrecognized_text": 1, "blank_line": 1}),
        dropped_line_diagnostics=[{"raw_line": "bad-line"}],
    )

    assert summary == {
        "total_lines": 3,
        "parsed_lines": 1,
        "dropped_lines": 2,
        "drop_ratio": 0.666667,
        "dropped_reasons": {
            "blank_line": 1,
            "unrecognized_text": 1,
        },
        "dropped_line_diagnostics": [{"raw_line": "bad-line"}],
    }

    without_diagnostics = parser_module._build_parse_summary(
        total_lines=0,
        parsed_lines=0,
        dropped_reasons=Counter(),
    )

    assert without_diagnostics == {
        "total_lines": 0,
        "parsed_lines": 0,
        "dropped_lines": 0,
        "drop_ratio": 0.0,
        "dropped_reasons": {},
    }



def test_build_dropped_line_diagnostic_exposes_public_fields():
    assert parser_module._build_dropped_line_diagnostic(
        source_path="-",
        line_number=4,
        reason="invalid_json",
        raw_line='{"timestamp":',
    ) == {
        "source_path": "-",
        "line_number": 4,
        "reason": "invalid_json",
        "raw_line": '{"timestamp":',
    }



def test_parse_json_line():
    line = '{"timestamp":"2025-01-01T00:00:01Z","level":"ERROR","component":"db","message":"connection failed","correlation_id":"c-1"}'
    event = parse_line(line)
    assert event is not None
    assert event.level == "ERROR"
    assert event.component == "db"
    assert event.correlation_id == "c-1"


@pytest.mark.parametrize(
    (
        "payload",
        "expected_timestamp",
        "expected_source_timestamp",
        "expected_source_offset",
        "expected_level",
        "expected_component",
        "expected_message",
        "expected_correlation_id",
    ),
    [
        (
            {
                "time": "2025-01-01T02:00:01+02:00",
                "severity": "warn",
                "service": "payments",
                "msg": "slow response cid=msg-time",
            },
            "2025-01-01T00:00:01+00:00",
            "2025-01-01T02:00:01+02:00",
            "+02:00",
            "WARN",
            "payments",
            "slow response cid=msg-time",
            "msg-time",
        ),
        (
            {
                "ts": "2025-01-01T00:00:03Z",
                "lvl": "error",
                "logger": "worker.queue",
                "event": "job failed correlation_id=evt-ts",
            },
            "2025-01-01T00:00:03+00:00",
            "2025-01-01T00:00:03Z",
            "Z",
            "ERROR",
            "worker.queue",
            "job failed correlation_id=evt-ts",
            "evt-ts",
        ),
    ],
)
def test_parse_json_line_accepts_documented_alias_shapes(
    payload,
    expected_timestamp,
    expected_source_timestamp,
    expected_source_offset,
    expected_level,
    expected_component,
    expected_message,
    expected_correlation_id,
):
    event = parse_json_line(json.dumps(payload))

    assert event is not None
    assert event.timestamp.isoformat() == expected_timestamp
    assert event.source_timestamp == expected_source_timestamp
    assert event.source_offset == expected_source_offset
    assert event.level == expected_level
    assert event.component == expected_component
    assert event.message == expected_message
    assert event.correlation_id == expected_correlation_id



def test_parse_json_line_prefers_populated_primary_keys_over_aliases():
    event = parse_json_line(
        json.dumps(
            {
                "timestamp": "2025-01-01T00:00:01Z",
                "time": "2025-01-01T00:00:02Z",
                "ts": "2025-01-01T00:00:03Z",
                "level": "error",
                "severity": "warn",
                "lvl": "debug",
                "component": "api",
                "service": "worker",
                "logger": "gateway",
                "message": "primary message cid=from-message",
                "msg": "secondary message",
                "event": "tertiary message",
                "correlation_id": "cid-primary",
                "cid": "cid-secondary",
            }
        )
    )

    assert event is not None
    assert event.timestamp.isoformat() == "2025-01-01T00:00:01+00:00"
    assert event.level == "ERROR"
    assert event.component == "api"
    assert event.message == "primary message cid=from-message"
    assert event.correlation_id == "cid-primary"



def test_parse_json_line_falls_through_empty_alias_values_and_keeps_optional_defaults():
    event = parse_json_line(
        json.dumps(
            {
                "timestamp": "",
                "time": None,
                "ts": "2025-01-01T00:00:05Z",
                "level": "",
                "severity": None,
                "lvl": "error",
                "component": "",
                "service": None,
                "logger": "queue.worker",
                "message": "",
                "msg": None,
                "event": "processed cid=evt-5",
            }
        )
    )
    defaulted_event = parse_json_line(json.dumps({"ts": "2025-01-01T00:00:06Z", "event": "hello"}))

    assert event is not None
    assert event.timestamp.isoformat() == "2025-01-01T00:00:05+00:00"
    assert event.level == "ERROR"
    assert event.component == "queue.worker"
    assert event.message == "processed cid=evt-5"
    assert event.correlation_id == "evt-5"

    assert defaulted_event is not None
    assert defaulted_event.level == "INFO"
    assert defaulted_event.component == "unknown"
    assert defaulted_event.message == "hello"
    assert defaulted_event.correlation_id is None



def test_parse_json_line_with_reason_treats_empty_timestamp_aliases_as_missing_timestamp():
    event, reason = parser_module._parse_json_line_with_reason(
        json.dumps({"timestamp": "", "time": None, "ts": "", "message": "broken"})
    )

    assert event is None
    assert reason == "missing_timestamp"


@pytest.mark.parametrize(
    ("payload", "expected_correlation_id"),
    [
        (
            {
                "timestamp": "2025-01-01T00:00:07Z",
                "message": "failed cid=from-message",
                "correlation_id": "cid-primary",
                "cid": "cid-secondary",
            },
            "cid-primary",
        ),
        (
            {
                "timestamp": "2025-01-01T00:00:08Z",
                "message": "failed correlation_id=from-message",
                "correlation_id": "",
                "cid": "cid-secondary",
            },
            "cid-secondary",
        ),
        (
            {
                "timestamp": "2025-01-01T00:00:09Z",
                "message": "failed cid=from-message",
                "correlation_id": None,
                "cid": "",
            },
            "from-message",
        ),
        (
            {
                "timestamp": "2025-01-01T00:00:10Z",
                "message": "failed correlation_id=from-message",
            },
            "from-message",
        ),
    ],
)
def test_parse_json_line_correlation_id_precedence_and_fallbacks(payload, expected_correlation_id):
    event = parse_json_line(json.dumps(payload))

    assert event is not None
    assert event.correlation_id == expected_correlation_id



def test_parse_text_line():
    line = "2025-01-01T00:00:02Z [WARN] api: slow response cid=abc-1"
    event = parse_line(line)
    assert event is not None
    assert event.level == "WARN"
    assert event.component == "api"
    assert event.correlation_id == "abc-1"


def test_parse_stats_summary_and_dropped_reasons(tmp_path):
    sample = tmp_path / "sample.log"
    sample.write_text(
        "\n".join(
            [
                '{"timestamp":"2025-01-01T00:00:01Z","component":"api","message":"ok"}',
                "2025-01-01T00:00:02Z INFO worker: started",
                "",
                '{"timestamp":"bad-ts","message":"broken"}',
                '{"message":"missing timestamp"}',
                "not a log line",
            ]
        ),
        encoding="utf-8",
    )

    events, summary = parse_file_with_summary(sample)

    assert len(events) == 2
    assert summary == {
        "total_lines": 6,
        "parsed_lines": 2,
        "dropped_lines": 4,
        "drop_ratio": 0.666667,
        "dropped_reasons": {
            "blank_line": 1,
            "invalid_timestamp": 1,
            "missing_timestamp": 1,
            "unrecognized_text": 1,
        },
    }


def test_parse_stats_summary_with_dropped_diagnostics_is_deterministic_and_bounded(tmp_path):
    sample = tmp_path / "sample.log"
    sample.write_text(
        "\n".join(
            [
                '{"timestamp":"2025-01-01T00:00:01Z","component":"api","message":"ok"}',
                "",
                '{"timestamp":"bad-ts","message":"broken"}',
                "not a log line",
                '{"message":"missing timestamp"}',
            ]
        ),
        encoding="utf-8",
    )

    events, summary = parse_file_with_summary(sample, diagnostics_limit=2)

    assert len(events) == 1
    assert summary["dropped_line_diagnostics"] == [
        {
            "source_path": str(sample),
            "line_number": 2,
            "reason": "blank_line",
            "raw_line": "",
        },
        {
            "source_path": str(sample),
            "line_number": 3,
            "reason": "invalid_timestamp",
            "raw_line": '{"timestamp":"bad-ts","message":"broken"}',
        },
    ]


def test_parse_lines_with_summary_accepts_stable_stdin_source_label():
    events, summary = parse_lines_with_summary(
        ["bad-line", "2025-01-01T00:00:01Z INFO api: ok"],
        source_path="-",
        diagnostics_limit=1,
    )

    assert len(events) == 1
    assert events[0].source_path == "-"
    assert events[0].line_number == 2
    assert summary["dropped_line_diagnostics"] == [
        {
            "source_path": "-",
            "line_number": 1,
            "reason": "unrecognized_text",
            "raw_line": "bad-line",
        }
    ]



def test_parse_lines_with_summary_propagates_source_order_to_successful_events():
    events, summary = parse_lines_with_summary(
        [
            "bad-line",
            "2025-01-01T00:00:01Z INFO api: first",
            "2025-01-01T00:00:01Z INFO api: second",
        ],
        source_path="source-a.log",
        source_order=7,
        diagnostics_limit=1,
    )

    assert [(event.source_order, event.source_path, event.line_number, event.message) for event in events] == [
        (7, "source-a.log", 2, "first"),
        (7, "source-a.log", 3, "second"),
    ]
    assert summary["dropped_line_diagnostics"] == [
        {
            "source_path": "source-a.log",
            "line_number": 1,
            "reason": "unrecognized_text",
            "raw_line": "bad-line",
        }
    ]


def test_parse_file_with_summary_preserves_source_path_and_line_number_for_successful_events(tmp_path):
    sample = tmp_path / "sample.log"
    sample.write_text(
        "bad-line\n2025-01-01T00:00:01Z INFO api: ok\n2025-01-01T00:00:02Z ERROR db: failed\n",
        encoding="utf-8",
    )

    events, _ = parse_file_with_summary(sample)

    assert [(event.source_path, event.line_number) for event in events] == [
        (str(sample), 2),
        (str(sample), 3),
    ]


@pytest.mark.parametrize(
    ("line", "expected_reason"),
    [
        ("   ", "blank_line"),
        ('{"timestamp":', "invalid_json"),
        ('{"message":"missing timestamp"}', "missing_timestamp"),
        ('{"timestamp":"bad-ts","message":"broken"}', "invalid_timestamp"),
        ("2025-99-01T00:00:02Z INFO api: broken timestamp", "invalid_timestamp"),
        ("not a log line", "unrecognized_text"),
    ],
)
def test_parse_line_with_reason_classifies_documented_drop_boundaries(line, expected_reason):
    event, reason = parse_line_with_reason(line)

    assert event is None
    assert reason == expected_reason



def test_parse_json_line_with_reason_classifies_non_object_payloads():
    event, reason = parser_module._parse_json_line_with_reason('["not", "an", "object"]')

    assert event is None
    assert reason == "json_not_object"


def test_parse_line_with_reason_uses_unknown_fallback(monkeypatch):
    monkeypatch.setattr(parser_module, "_parse_text_line_with_reason", lambda _line: (None, None))

    event, reason = parse_line_with_reason("2025-01-01T00:00:01Z INFO api: hello")

    assert event is None
    assert reason == "unknown"


def test_parse_json_line_wrapper_exposes_event():
    line = '{"timestamp":"2025-01-01T00:00:01Z","component":"api","message":"ok"}'
    event = parse_json_line(line)

    assert event is not None
    assert event.component == "api"


def test_parse_text_line_wrapper_exposes_event():
    event = parse_text_line("2025-01-01T00:00:02Z INFO api: started")

    assert event is not None
    assert event.level == "INFO"


def test_parse_text_line_accepts_offset_and_normalizes_to_utc():
    line = "2025-01-01T02:00:02+02:00 [WARN] api: slow response cid=abc-1"
    event = parse_line(line)

    assert event is not None
    assert event.timestamp.isoformat() == "2025-01-01T00:00:02+00:00"
    assert event.source_timestamp == "2025-01-01T02:00:02+02:00"
    assert event.source_offset == "+02:00"


def test_parse_json_line_normalizes_negative_offset_to_utc():
    line = (
        '{"timestamp":"2024-12-31T19:00:07-05:00","level":"ERROR",'
        '"component":"api","message":"failed"}'
    )
    event = parse_line(line)

    assert event is not None
    assert event.timestamp.isoformat() == "2025-01-01T00:00:07+00:00"
    assert event.source_timestamp == "2024-12-31T19:00:07-05:00"
    assert event.source_offset == "-05:00"


def test_parse_text_line_provenance_uses_z_offset_marker():
    line = "2025-01-01T00:00:02Z INFO api: started"
    event = parse_line(line)

    assert event is not None
    assert event.source_timestamp == "2025-01-01T00:00:02Z"
    assert event.source_offset == "Z"


def test_parse_json_line_provenance_has_null_offset_for_naive_timestamp():
    line = '{"timestamp":"2025-01-01 00:00:02","component":"api","message":"ok"}'
    event = parse_line(line)

    assert event is not None
    assert event.timestamp.isoformat() == "2025-01-01T00:00:02+00:00"
    assert event.source_timestamp == "2025-01-01 00:00:02"
    assert event.source_offset is None
    assert event.to_dict()["source_offset"] is None


def test_parse_event_contract_keys_are_stable_for_current_schema_version():
    line = '{"timestamp":"2025-01-01T00:00:01Z","component":"api","message":"ok"}'
    event = parse_line(line)

    assert event is not None
    assert set(event.to_dict().keys()) == {
        "timestamp",
        "source_timestamp",
        "source_offset",
        "source_path",
        "line_number",
        "level",
        "component",
        "message",
        "correlation_id",
    }


def test_parse_file_stream_does_not_call_read_text(tmp_path, monkeypatch):
    sample = tmp_path / "sample.log"
    sample.write_text("2025-01-01T00:00:01Z INFO api: ok\n", encoding="utf-8")

    def _fail_read_text(self: Path, *args, **kwargs):
        raise AssertionError("parse_file_with_summary should stream lines, not call read_text")

    monkeypatch.setattr(Path, "read_text", _fail_read_text)

    events, summary = parse_file_with_summary(sample)

    assert len(events) == 1
    assert summary["total_lines"] == 1
    assert summary["parsed_lines"] == 1


def test_parse_file_stream_large_input_summary(tmp_path):
    sample = tmp_path / "large.log"
    valid_line = "2025-01-01T00:00:00Z INFO api: ok cid=c-1\n"
    invalid_line = "not a log line\n"

    with sample.open("w", encoding="utf-8") as handle:
        for _ in range(5_000):
            handle.write(valid_line)
            handle.write(invalid_line)

    events, summary = parse_file_with_summary(sample)

    assert len(events) == 5_000
    assert summary == {
        "total_lines": 10_000,
        "parsed_lines": 5_000,
        "dropped_lines": 5_000,
        "drop_ratio": 0.5,
        "dropped_reasons": {"unrecognized_text": 5_000},
    }
