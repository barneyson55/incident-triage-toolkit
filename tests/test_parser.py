from triage_toolkit.parser import parse_file_with_summary, parse_line, parse_line_with_reason


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
