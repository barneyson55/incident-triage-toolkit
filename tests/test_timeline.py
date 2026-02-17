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


def test_timeline_mixed_timezone_offsets_render_in_utc():
    lines = [
        "2025-01-01T00:00:10Z INFO api: z time",
        "2025-01-01T02:00:05+02:00 INFO api: plus two",
        "2024-12-31T19:00:07-05:00 ERROR worker: minus five",
    ]
    events = [parse_line(line) for line in lines]
    timeline = build_timeline([event for event in events if event])

    assert "T0: `2025-01-01T00:00:05+00:00`" in timeline
    assert "2025-01-01T00:00:05+00:00" in timeline
    assert "2025-01-01T00:00:07+00:00" in timeline
    assert "2025-01-01T00:00:10+00:00" in timeline

    first = timeline.find("2025-01-01T00:00:05+00:00")
    second = timeline.find("2025-01-01T00:00:07+00:00")
    third = timeline.find("2025-01-01T00:00:10+00:00")
    assert 0 <= first < second < third
    assert "+02:00" not in timeline
    assert "-05:00" not in timeline
