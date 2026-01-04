from triage_toolkit.parser import parse_line


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
