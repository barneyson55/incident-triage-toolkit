from pathlib import Path

import triage_toolkit.parser as parser_module
from triage_toolkit.parser import (
    parse_file_with_summary,
    parse_json_line,
    parse_line,
    parse_line_with_reason,
    parse_text_line,
)


def test_parse_json_line():
    line = '{"timestamp":"2025-01-01T00:00:01Z","level":"ERROR","component":"db","message":"connection failed","correlation_id":"c-1"}'
    event = parse_line(line)
    assert event is not None
    assert event.level == "ERROR"
    assert event.component == "db"
    assert event.correlation_id == "c-1"


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


def test_parse_dropped_reason_for_invalid_json():
    event, reason = parse_line_with_reason('{"timestamp":')
    assert event is None
    assert reason == "invalid_json"


def test_parse_dropped_reason_for_json_not_object():
    event, reason = parser_module._parse_json_line_with_reason('["not", "an", "object"]')
    assert event is None
    assert reason == "json_not_object"


def test_parse_text_line_invalid_timestamp_reason():
    event, reason = parse_line_with_reason("2025-99-01T00:00:02Z INFO api: broken timestamp")
    assert event is None
    assert reason == "invalid_timestamp"


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


def test_parse_json_line_normalizes_negative_offset_to_utc():
    line = (
        '{"timestamp":"2024-12-31T19:00:07-05:00","level":"ERROR",'
        '"component":"api","message":"failed"}'
    )
    event = parse_line(line)

    assert event is not None
    assert event.timestamp.isoformat() == "2025-01-01T00:00:07+00:00"


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
