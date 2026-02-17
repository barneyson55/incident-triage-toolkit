from triage_toolkit.parser import parse_line
from triage_toolkit.runbook import build_runbook


def test_runbook_headings():
    lines = [
        "2025-01-01T00:00:01Z ERROR api: failed request cid=c-1",
        "2025-01-01T00:00:02Z INFO api: recovered cid=c-1",
    ]
    events = [parse_line(line) for line in lines]
    runbook = build_runbook([event for event in events if event], "Incident: Sample")
    for heading in [
        "## Symptoms",
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
    assert "+02:00" not in runbook
    assert "-05:00" not in runbook
