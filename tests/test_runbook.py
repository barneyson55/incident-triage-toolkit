from pathlib import Path

from triage_toolkit.parser import parse_file_with_summary, parse_line
from triage_toolkit.runbook import build_runbook

GOLDEN_DIR = Path(__file__).parent / "fixtures" / "golden"


def test_runbook_headings():
    lines = [
        "2025-01-01T00:00:01Z ERROR api: failed request cid=c-1",
        "2025-01-01T00:00:02Z INFO api: recovered cid=c-1",
    ]
    events = [parse_line(line) for line in lines]
    runbook = build_runbook([event for event in events if event], "Incident: Sample")
    for heading in [
        "## Symptoms",
        "## Evidence",
        "## Checks",
        "## Workaround",
        "## Fix/Escalation",
        "## Verification",
        "## Notes",
    ]:
        assert heading in runbook


def test_runbook_first_observed_is_normalized_to_utc():
    lines = [
        "2025-01-01T02:00:01+02:00 ERROR api: failed request",
        "2024-12-31T19:00:02-05:00 INFO api: recovered",
    ]
    events = [parse_line(line) for line in lines]
    runbook = build_runbook([event for event in events if event], "Incident: Sample")

    assert "- First observed: `2025-01-01T00:00:01+00:00`" in runbook
    assert "- Last observed: `2025-01-01T00:00:02+00:00`" in runbook
    assert "+02:00" not in runbook
    assert "-05:00" not in runbook


def test_runbook_filtered_subset_uses_filtered_first_observed_and_counts():
    lines = [
        "2025-01-01T00:00:01Z INFO api: accepted cid=c-1",
        "2025-01-01T00:00:02Z ERROR api: timeout cid=c-2",
        "2025-01-01T00:00:03Z ERROR worker: timeout cid=c-2",
    ]
    events = [parse_line(line) for line in lines]
    filtered = [event for event in events if event and event.correlation_id == "c-2"]

    runbook = build_runbook(filtered, "Incident: Filtered")

    assert "- First observed: `2025-01-01T00:00:02+00:00`" in runbook
    assert "- Last observed: `2025-01-01T00:00:03+00:00`" in runbook
    assert "- Evidence events: 2 of 2 total" in runbook
    assert "- Suspected components: api (1), worker (1)" in runbook
    assert "- Representative correlation IDs: `c-2`" in runbook


def test_runbook_evidence_sections_are_deterministic_and_use_earliest_example_per_signature():
    lines = [
        "2025-01-01T00:00:04Z CRITICAL db: query failed cid=q-10",
        "2025-01-01T00:00:03Z ERROR api: timeout cid=c-2",
        "2025-01-01T00:00:01Z ERROR db: query failed cid=q-9",
        "2025-01-01T00:00:02Z ERROR worker: timeout cid=c-2",
    ]
    events = [parse_line(line) for line in lines]
    runbook = build_runbook([event for event in events if event], "Incident: Evidence")

    assert "- Top error signatures: `query failed cid=<id>` (2), `timeout cid=<id>` (2)" in runbook
    assert "- query failed cid=<id> (count: 2, first: 2025-01-01T00:00:01+00:00, last: 2025-01-01T00:00:04+00:00, components: db, example: `n/a`)" in runbook
    assert "- timeout cid=<id> (count: 2, first: 2025-01-01T00:00:02+00:00, last: 2025-01-01T00:00:03+00:00, components: worker, api, example: `n/a`)" in runbook
    assert "- `2025-01-01T00:00:01+00:00` `ERROR` `db` — query failed cid=q-9 (source: `n/a`)" in runbook
    assert "- `2025-01-01T00:00:02+00:00` `ERROR` `worker` — timeout cid=c-2 (source: `n/a`)" in runbook
    assert "query failed cid=q-10" not in runbook


def test_runbook_surfaces_source_provenance_in_evidence_and_examples(tmp_path):
    sample = tmp_path / "sample.log"
    sample.write_text(
        "2025-01-01T00:00:01Z ERROR api: failed request cid=c-1\n2025-01-01T00:00:02Z INFO api: recovered cid=c-1\n",
        encoding="utf-8",
    )

    events, _ = parse_file_with_summary(sample)
    runbook = build_runbook(events, "Incident: Provenance")

    assert f"- failed request cid=<id> (count: 1, first: 2025-01-01T00:00:01+00:00, last: 2025-01-01T00:00:01+00:00, components: api, example: `{sample}:1`)" in runbook
    assert f"- `2025-01-01T00:00:01+00:00` `ERROR` `api` — failed request cid=c-1 (source: `{sample}:1`)" in runbook


def test_runbook_empty_state_uses_explicit_no_evidence_template():
    runbook = build_runbook([], "Incident: Empty")

    assert "- Incident window: `n/a`" in runbook
    assert "- Evidence events: 0 of 0 total" in runbook
    assert "- Top error signatures: none" in runbook
    assert "- Suspected components: none" in runbook
    assert "- Representative correlation IDs: none" in runbook
    assert "- No parsed events matched the selected inputs or filters." in runbook
    assert "- None detected in parsed input." in runbook
    assert "- No representative failures available." in runbook


def test_runbook_uses_shared_incident_evidence_rules_for_critical_fatal_and_message_hints():
    lines = [
        "2025-01-01T00:00:01Z INFO api: accepted",
        "2025-01-01T00:00:02Z CRITICAL db: query failed cid=q-1",
        "2025-01-01T00:00:03Z FATAL worker: crash loop 42",
        "2025-01-01T00:00:04Z INFO web: upstream error on request 99",
    ]
    events = [parse_line(line) for line in lines]
    runbook = build_runbook([event for event in events if event], "Incident: Evidence Semantics")

    assert "- Evidence events: 3 of 4 total" in runbook
    assert "- Top error signatures: `query failed cid=<id>` (1), `crash loop #` (1), `upstream error on request #` (1)" in runbook
    assert "- Suspected components: db (1), worker (1), web (1)" in runbook
    assert "- `2025-01-01T00:00:02+00:00` `CRITICAL` `db` — query failed cid=q-1 (source: `n/a`)" in runbook
    assert "- `2025-01-01T00:00:03+00:00` `FATAL` `worker` — crash loop 42 (source: `n/a`)" in runbook
    assert "- `2025-01-01T00:00:04+00:00` `INFO` `web` — upstream error on request 99 (source: `n/a`)" in runbook


def test_runbook_surfaces_ranked_evidence_by_source(tmp_path):
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
    runbook = build_runbook(events_a + events_c + events_b, "Incident: Sources")

    assert (
        f"- Evidence by source: `{source_a}` (2 of 4), `{source_b}` (1 of 4), `{source_c}` (1 of 4)"
        in runbook
    )
    assert "### Evidence by Source" in runbook
    first = runbook.index(f"- `{source_a}` (evidence: 2 of 4, first: 2025-01-01T00:00:01+00:00)")
    second = runbook.index(f"- `{source_b}` (evidence: 1 of 4, first: 2025-01-01T00:00:02+00:00)")
    third = runbook.index(f"- `{source_c}` (evidence: 1 of 4, first: 2025-01-01T00:00:02+00:00)")
    assert first < second < third


def test_runbook_redaction_masks_signatures_examples_and_correlation_ids_deterministically():
    lines = [
        (
            "2025-01-01T00:00:01Z ERROR api: notify alice@example.com from 10.2.3.4 "
            "cid=550e8400-e29b-41d4-a716-446655440000 token=AbCdEfGhIjKlMnOpQrSt123456"
        )
    ]
    events = [parse_line(line) for line in lines]
    runbook = build_runbook([event for event in events if event], "Incident: Redacted", redact=True)

    assert "alice@example.com" not in runbook
    assert "10.2.3.4" not in runbook
    assert "550e8400-e29b-41d4-a716-446655440000" not in runbook
    assert "AbCdEfGhIjKlMnOpQrSt123456" not in runbook
    assert "[redacted-email:" in runbook
    assert "[redacted-ip:" in runbook
    assert "[redacted-id:" in runbook
    assert "[redacted-secret:" in runbook


def test_runbook_golden_output_is_deterministic():
    sample = GOLDEN_DIR / "mixed_input.log"
    expected = (GOLDEN_DIR / "runbook_output.md").read_text(encoding="utf-8")

    events, _ = parse_file_with_summary(sample)
    actual = build_runbook(events, "Incident: Golden")

    assert actual == expected
