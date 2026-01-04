from triage_toolkit.parser import parse_line
from triage_toolkit.timeline import build_timeline


def test_timeline_ordering():
    lines = [
        "2025-01-01T00:00:05Z INFO api: later event cid=c-1",
        "2025-01-01T00:00:01Z ERROR api: earlier error cid=c-2",
    ]
    events = [parse_line(line) for line in lines]
    timeline = build_timeline([event for event in events if event])
    first_index = timeline.find("2025-01-01T00:00:01")
    second_index = timeline.find("2025-01-01T00:00:05")
    assert 0 <= first_index < second_index
    assert "T0:" in timeline
