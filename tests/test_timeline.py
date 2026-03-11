from pathlib import Path

from triage_toolkit.parser import parse_file_with_summary, parse_line
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

    worker_index = timeline.find("| 2025-01-01T00:00:02+00:00 | n/a | ERROR | worker | timeout cid=c-2 |")
    api_index = timeline.find("| 2025-01-01T00:00:02+00:00 | n/a | ERROR | api | timeout cid=c-2 |")
    assert 0 <= worker_index < api_index


def test_timeline_surfaces_source_provenance_in_event_rows(tmp_path):
    sample = tmp_path / "sample.log"
    sample.write_text(
        "2025-01-01T00:00:01Z INFO api: accepted\n2025-01-01T00:00:02Z ERROR db: failed\n",
        encoding="utf-8",
    )

    events, _ = parse_file_with_summary(sample)
    timeline = build_timeline(events)

    assert f"| 2025-01-01T00:00:01+00:00 | {sample}:1 | INFO | api | accepted |" in timeline
    assert f"| 2025-01-01T00:00:02+00:00 | {sample}:2 | ERROR | db | failed |" in timeline


def test_timeline_includes_critical_fatal_and_message_hint_events_in_shared_evidence_sections():
    lines = [
        "2025-01-01T00:00:01Z INFO api: accepted",
        "2025-01-01T00:00:02Z CRITICAL db: query failed cid=q-1",
        "2025-01-01T00:00:03Z FATAL worker: crash loop 42",
        "2025-01-01T00:00:04Z INFO web: upstream error on request 99",
    ]
    events = [parse_line(line) for line in lines]
    timeline = build_timeline([event for event in events if event])

    assert "- query failed cid=<id> (count: 1, first: 2025-01-01T00:00:02+00:00, last: 2025-01-01T00:00:02+00:00)" in timeline
    assert "- crash loop # (count: 1, first: 2025-01-01T00:00:03+00:00, last: 2025-01-01T00:00:03+00:00)" in timeline
    assert "- upstream error on request # (count: 1, first: 2025-01-01T00:00:04+00:00, last: 2025-01-01T00:00:04+00:00)" in timeline
    assert "- db (errors: 1)" in timeline
    assert "- worker (errors: 1)" in timeline
    assert "- web (errors: 1)" in timeline


def test_timeline_redaction_masks_rendered_messages_and_signatures_deterministically():
    lines = [
        (
            "2025-01-01T00:00:01Z ERROR api: notify alice@example.com from 10.2.3.4 "
            "cid=550e8400-e29b-41d4-a716-446655440000 token=AbCdEfGhIjKlMnOpQrSt123456"
        )
    ]
    events = [parse_line(line) for line in lines]
    timeline = build_timeline([event for event in events if event], redact=True)

    assert "alice@example.com" not in timeline
    assert "10.2.3.4" not in timeline
    assert "550e8400-e29b-41d4-a716-446655440000" not in timeline
    assert "AbCdEfGhIjKlMnOpQrSt123456" not in timeline
    assert "[redacted-email:" in timeline
    assert "[redacted-ip:" in timeline
    assert "[redacted-id:" in timeline
    assert "[redacted-secret:" in timeline


def test_timeline_golden_output_is_deterministic():
    sample = GOLDEN_DIR / "mixed_input.log"
    expected = (GOLDEN_DIR / "timeline_output.md").read_text(encoding="utf-8")

    events, _ = parse_file_with_summary(sample)
    actual = build_timeline(events)

    assert actual == expected
