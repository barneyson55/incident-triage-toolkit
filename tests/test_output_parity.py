import json
import re
from pathlib import Path

from typer.testing import CliRunner

from triage_toolkit.cli import app

runner = CliRunner()
REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURE_DIR = Path("tests/fixtures/parity")
_TIMELINE_ROW_RE = re.compile(
    r"^\| (?P<timestamp>\d{4}-\d{2}-\d{2}T[^|]+) \| (?P<source>[^|]+) \| (?P<level>[^|]+) \| (?P<component>[^|]+) \| (?P<message>.+) \|$"
)
_TIMELINE_SIGNATURE_RE = re.compile(
    r"^- (?P<name>.+) \(count: (?P<count>\d+), first: (?P<first>[^,]+), last: (?P<last>[^)]+)\)$"
)
_RUNBOOK_SIGNATURE_RE = re.compile(
    r"^- (?P<name>.+) \(count: (?P<count>\d+), first: (?P<first>[^,]+), last: (?P<last>[^,]+), components: .*?, example: `.*`\)$"
)
_SOURCE_RE = re.compile(
    r"^- `(?P<source>.+)` \(evidence: (?P<count>\d+) of (?P<total>\d+), first: (?P<first>[^)]+)\)$"
)


def _invoke(command: str, args: list[str], *, stdin: str | None = None, monkeypatch):
    monkeypatch.chdir(REPO_ROOT)
    argv = [command, *args, "--out", "-"]
    if command == "runbook":
        argv.extend(["--title", "Incident: Parity"])

    result = runner.invoke(app, argv, input=stdin)

    assert result.exit_code == 0, result.output
    if command == "summary":
        return json.loads(result.stdout)
    return result.stdout


def _section_lines(markdown: str, heading: str) -> list[str]:
    lines = markdown.splitlines()
    start = lines.index(heading) + 1
    collected: list[str] = []
    for line in lines[start:]:
        if line.startswith("## ") or line.startswith("### "):
            break
        if line.startswith("- "):
            collected.append(line)
    return collected


def _normalize_timestamp(value: str | None) -> str | None:
    if value in {None, "n/a"}:
        return None
    return value


def _summary_snapshot(payload: dict[str, object]) -> dict[str, object]:
    incident_window = payload["incident_window"]
    return {
        "first": incident_window["start"],
        "last": incident_window["end"],
        "evidence_count": payload["error_count"],
        "signatures": [
            (item["name"], item["count"])
            for item in payload["top_error_signatures"]
        ],
        "sources": [
            (item["source"], item["count"])
            for item in payload["evidence_by_source"]
        ],
    }


def _timeline_snapshot(markdown: str) -> dict[str, object]:
    event_rows = [
        match.groupdict()
        for line in markdown.splitlines()
        if (match := _TIMELINE_ROW_RE.match(line))
    ]

    signature_lines = _section_lines(markdown, "## Notable Errors")
    if signature_lines == ["- None detected in parsed input."]:
        signatures: list[tuple[str, int]] = []
    else:
        signatures = [
            (match.group("name"), int(match.group("count")))
            for line in signature_lines
            if (match := _TIMELINE_SIGNATURE_RE.match(line))
        ]

    source_lines = _section_lines(markdown, "## Evidence by Source")
    if source_lines == ["- No source concentration inferred."]:
        sources: list[tuple[str, int]] = []
    else:
        sources = [
            (match.group("source"), int(match.group("count")))
            for line in source_lines
            if (match := _SOURCE_RE.match(line))
        ]

    return {
        "first": event_rows[0]["timestamp"] if event_rows else None,
        "last": event_rows[-1]["timestamp"] if event_rows else None,
        "evidence_count": len(event_rows),
        "signatures": signatures,
        "sources": sources,
    }


def _runbook_value(markdown: str, label: str) -> str | None:
    match = re.search(rf"^- {re.escape(label)}: `([^`]+)`$", markdown, re.MULTILINE)
    assert match is not None
    return _normalize_timestamp(match.group(1))


def _runbook_snapshot(markdown: str) -> dict[str, object]:
    evidence_match = re.search(r"^- Evidence events: (\d+) of (\d+) total$", markdown, re.MULTILINE)
    assert evidence_match is not None

    signature_lines = _section_lines(markdown, "### Top Error Signatures")
    if signature_lines == ["- None detected in parsed input."]:
        signatures: list[tuple[str, int]] = []
    else:
        signatures = [
            (match.group("name"), int(match.group("count")))
            for line in signature_lines
            if (match := _RUNBOOK_SIGNATURE_RE.match(line))
        ]

    source_lines = _section_lines(markdown, "### Evidence by Source")
    if source_lines == ["- None detected in parsed input."]:
        sources: list[tuple[str, int]] = []
    else:
        sources = [
            (match.group("source"), int(match.group("count")))
            for line in source_lines
            if (match := _SOURCE_RE.match(line))
        ]

    return {
        "first": _runbook_value(markdown, "First observed"),
        "last": _runbook_value(markdown, "Last observed"),
        "evidence_count": int(evidence_match.group(1)),
        "signatures": signatures,
        "sources": sources,
    }


def _assert_surface_parity(args: list[str], *, stdin: str | None = None, monkeypatch) -> dict[str, object]:
    summary = _summary_snapshot(_invoke("summary", args, stdin=stdin, monkeypatch=monkeypatch))
    timeline = _timeline_snapshot(_invoke("timeline", args, stdin=stdin, monkeypatch=monkeypatch))
    runbook = _runbook_snapshot(_invoke("runbook", args, stdin=stdin, monkeypatch=monkeypatch))

    assert timeline == summary
    assert runbook == summary
    return summary


def test_filtered_multi_input_fixture_keeps_summary_timeline_and_runbook_aligned(monkeypatch):
    args = [
        str(FIXTURE_DIR / "parity_multi_a.log"),
        str(FIXTURE_DIR / "parity_multi_b.log"),
        "--component",
        "api",
        "--component",
        "worker",
        "--level",
        "error",
    ]

    snapshot = _assert_surface_parity(args, monkeypatch=monkeypatch)

    assert snapshot == {
        "first": "2025-01-01T00:00:02+00:00",
        "last": "2025-01-01T00:00:05+00:00",
        "evidence_count": 4,
        "signatures": [
            ("timeout on checkout cid=<id>", 3),
            ("queue stalled cid=<id>", 1),
        ],
        "sources": [
            (str(FIXTURE_DIR / "parity_multi_a.log"), 2),
            (str(FIXTURE_DIR / "parity_multi_b.log"), 2),
        ],
    }


def test_filtered_file_and_stdin_fixture_keeps_summary_timeline_and_runbook_aligned(monkeypatch):
    args = [
        str(FIXTURE_DIR / "parity_stdin_file.log"),
        "-",
        "--component",
        "api",
        "--component",
        "worker",
        "--level",
        "error",
    ]
    stdin = (
        "2025-01-01T00:00:02Z ERROR worker: timeout on checkout cid=c-2\n"
        "2025-01-01T00:00:04Z ERROR worker: queue stalled cid=q-1\n"
    )

    snapshot = _assert_surface_parity(args, stdin=stdin, monkeypatch=monkeypatch)

    assert snapshot == {
        "first": "2025-01-01T00:00:02+00:00",
        "last": "2025-01-01T00:00:04+00:00",
        "evidence_count": 3,
        "signatures": [
            ("timeout on checkout cid=<id>", 2),
            ("queue stalled cid=<id>", 1),
        ],
        "sources": [
            ("-", 2),
            (str(FIXTURE_DIR / "parity_stdin_file.log"), 1),
        ],
    }


def test_empty_filtered_slice_keeps_summary_timeline_and_runbook_empty_states_aligned(monkeypatch):
    args = [
        str(FIXTURE_DIR / "parity_multi_a.log"),
        str(FIXTURE_DIR / "parity_multi_b.log"),
        "--component",
        "cache",
    ]

    snapshot = _assert_surface_parity(args, monkeypatch=monkeypatch)
    timeline = _invoke("timeline", args, monkeypatch=monkeypatch)
    runbook = _invoke("runbook", args, monkeypatch=monkeypatch)

    assert snapshot == {
        "first": None,
        "last": None,
        "evidence_count": 0,
        "signatures": [],
        "sources": [],
    }
    assert "_No events parsed._" in timeline
    assert "- None detected in parsed input." in timeline
    assert "- No source concentration inferred." in timeline
    assert "- No parsed events matched the selected inputs or filters." in runbook
    assert "- None detected in parsed input." in runbook
    assert "- No representative failures available." in runbook
