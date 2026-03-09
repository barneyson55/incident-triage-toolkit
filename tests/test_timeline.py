from pathlib import Path

from triage_toolkit.parser import parse_line
from triage_toolkit.timeline import build_timeline

GOLDEN_DIR = Path(__file__).parent / "fixtures" / "golden"


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


def test_timeline_filtered_subset_preserves_stable_order_for_tied_timestamps():
    lines = [
        "2025-01-01T00:00:02Z ERROR worker: timeout cid=c-2",
        "2025-01-01T00:00:02Z ERROR api: timeout cid=c-2",
        "2025-01-01T00:00:03Z ERROR web: timeout cid=c-3",
    ]
    events = [parse_line(line) for line in lines]
    filtered = [event for event in events if event and event.correlation_id == "c-2"]

    timeline = build_timeline(filtered)

    worker_index = timeline.find("| 2025-01-01T00:00:02+00:00 | ERROR | worker | timeout cid=c-2 |")
    api_index = timeline.find("| 2025-01-01T00:00:02+00:00 | ERROR | api | timeout cid=c-2 |")
    assert 0 <= worker_index < api_index


def test_timeline_golden_output_is_deterministic():
    lines = (GOLDEN_DIR / "mixed_input.log").read_text(encoding="utf-8").splitlines()
    expected = (GOLDEN_DIR / "timeline_output.md").read_text(encoding="utf-8")

    events = [parse_line(line) for line in lines]
    actual = build_timeline([event for event in events if event])

    assert actual == expected
