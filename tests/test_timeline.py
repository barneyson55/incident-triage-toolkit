import json
from dataclasses import replace
from pathlib import Path

from triage_toolkit.parser import parse_file_with_summary, parse_line, parse_lines_with_summary
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


def test_timeline_deterministic_filtered_slice_uses_explicit_source_order_for_same_timestamp_multi_input(tmp_path):
    source_a = tmp_path / "a.log"
    source_b = tmp_path / "b.log"
    source_a.write_text(
        "2025-01-01T00:00:02Z ERROR api: timeout cid=c-2\n",
        encoding="utf-8",
    )
    source_b.write_text(
        "2025-01-01T00:00:02Z ERROR worker: timeout cid=c-2\n",
        encoding="utf-8",
    )

    events_a, _ = parse_file_with_summary(source_a, source_order=0)
    events_b, _ = parse_file_with_summary(source_b, source_order=1)
    filtered = [event for event in (events_b + events_a) if event.correlation_id == "c-2"]

    timeline = build_timeline(filtered)

    api_index = timeline.find(f"| 2025-01-01T00:00:02+00:00 | {source_a}:1 | ERROR | api | timeout cid=c-2 |")
    worker_index = timeline.find(
        f"| 2025-01-01T00:00:02+00:00 | {source_b}:1 | ERROR | worker | timeout cid=c-2 |"
    )
    assert 0 <= api_index < worker_index


def test_timeline_deterministic_filtered_slice_uses_explicit_source_order_for_same_timestamp_file_and_stdin(tmp_path):
    source_file = tmp_path / "file.log"
    source_file.write_text(
        "2025-01-01T00:00:02Z ERROR api: timeout cid=c-2\n",
        encoding="utf-8",
    )

    file_events, _ = parse_file_with_summary(source_file, source_order=0)
    stdin_events, _ = parse_lines_with_summary(
        ["2025-01-01T00:00:02Z ERROR worker: timeout cid=c-2"],
        source_path="-",
        source_order=1,
    )
    filtered = [event for event in (stdin_events + file_events) if event.correlation_id == "c-2"]

    timeline = build_timeline(filtered)

    file_index = timeline.find(
        f"| 2025-01-01T00:00:02+00:00 | {source_file}:1 | ERROR | api | timeout cid=c-2 |"
    )
    stdin_index = timeline.find("| 2025-01-01T00:00:02+00:00 | -:1 | ERROR | worker | timeout cid=c-2 |")
    assert 0 <= file_index < stdin_index


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


def test_timeline_markdown_cells_escape_pipes_and_flatten_newlines():
    parsed = parse_line(
        json.dumps(
            {
                "timestamp": "2025-01-01T00:00:01Z",
                "level": "error",
                "component": "api|edge\nblue",
                "message": "timeout|while\nprocessing",
            }
        )
    )
    assert parsed is not None

    event = replace(parsed, source_path="ops|primary\nfeed", line_number=7)
    fallback = replace(parsed, source_path=None, line_number=None)

    timeline = build_timeline([event, fallback])

    assert (
        "| 2025-01-01T00:00:01+00:00 | ops\\|primary feed:7 | ERROR | api\\|edge blue | timeout\\|while processing |"
        in timeline
    )
    assert "- timeout\\|while processing (count: 2, first: 2025-01-01T00:00:01+00:00, last: 2025-01-01T00:00:01+00:00)" in timeline
    assert "- `ops\\|primary feed` (evidence: 1 of 2, first: 2025-01-01T00:00:01+00:00)" in timeline
    assert "- api\\|edge blue (errors: 2)" in timeline
    assert "| 2025-01-01T00:00:01+00:00 | n/a | ERROR | api\\|edge blue | timeout\\|while processing |" in timeline
    assert "ops|primary\nfeed" not in timeline
    assert "api|edge\nblue" not in timeline
    assert "timeout|while\nprocessing" not in timeline


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


def test_timeline_surfaces_ranked_evidence_by_source(tmp_path):
    source_a = tmp_path / "a.log"
    source_b = tmp_path / "b.log"
    source_c = tmp_path / "c.log"
    source_a.write_text(
        "2025-01-01T00:00:01Z ERROR api: failed-a-1\n2025-01-01T00:00:04Z ERROR api: failed-a-2\n",
        encoding="utf-8",
    )
    source_b.write_text("2025-01-01T00:00:02Z ERROR db: failed-b\n", encoding="utf-8")
    source_c.write_text("2025-01-01T00:00:02Z ERROR worker: failed-c\n", encoding="utf-8")

    events_a, _ = parse_file_with_summary(source_a)
    events_b, _ = parse_file_with_summary(source_b)
    events_c, _ = parse_file_with_summary(source_c)
    timeline = build_timeline(events_a + events_c + events_b)

    assert "## Evidence by Source" in timeline
    first = timeline.index(f"- `{source_a}` (evidence: 2 of 4, first: 2025-01-01T00:00:01+00:00)")
    second = timeline.index(f"- `{source_b}` (evidence: 1 of 4, first: 2025-01-01T00:00:02+00:00)")
    third = timeline.index(f"- `{source_c}` (evidence: 1 of 4, first: 2025-01-01T00:00:02+00:00)")
    assert first < second < third


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


def test_timeline_redacted_golden_output_is_deterministic():
    sample = GOLDEN_DIR / "redacted_input.log"
    expected = (GOLDEN_DIR / "timeline_output_redacted.md").read_text(encoding="utf-8")

    events, _ = parse_file_with_summary(sample)
    actual = build_timeline(events, redact=True)

    assert actual == expected


def test_timeline_golden_output_is_deterministic():
    sample = GOLDEN_DIR / "mixed_input.log"
    expected = (GOLDEN_DIR / "timeline_output.md").read_text(encoding="utf-8")

    events, _ = parse_file_with_summary(sample)
    actual = build_timeline(events)

    assert actual == expected
