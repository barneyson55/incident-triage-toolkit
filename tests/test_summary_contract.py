import json
from pathlib import Path

from typer.testing import CliRunner

import triage_toolkit.cli as cli_module
from triage_toolkit.cli import app

runner = CliRunner()
REPO_ROOT = Path(__file__).resolve().parent.parent
GOLDEN_DIR = Path(__file__).parent / "fixtures" / "golden"


def _golden(name: str) -> str:
    return (GOLDEN_DIR / name).read_text(encoding="utf-8")


def test_summary_contract_required_top_level_keys_for_current_schema(monkeypatch):
    monkeypatch.chdir(REPO_ROOT)

    result = runner.invoke(app, ["summary", "tests/fixtures/golden/mixed_input.log", "--out", "-"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["schema_version"] == cli_module.SUMMARY_SCHEMA_VERSION
    assert set(payload.keys()) == {
        "schema_version",
        "incident_window",
        "event_count",
        "error_count",
        "top_components",
        "top_error_signatures",
        "evidence_by_source",
        "correlation_id_coverage",
        "parse_summary",
    }


def test_summary_golden_single_input_output_is_deterministic(monkeypatch):
    monkeypatch.chdir(REPO_ROOT)

    result = runner.invoke(app, ["summary", "tests/fixtures/golden/mixed_input.log", "--out", "-"])

    assert result.exit_code == 0
    assert result.stdout == _golden("summary_output_single.json")


def test_summary_golden_multi_input_output_is_deterministic(monkeypatch):
    monkeypatch.chdir(REPO_ROOT)

    result = runner.invoke(
        app,
        [
            "summary",
            "tests/fixtures/golden/summary_multi_a.log",
            "tests/fixtures/golden/summary_multi_b.log",
            "--out",
            "-",
        ],
    )

    assert result.exit_code == 0
    assert result.stdout == _golden("summary_output_multi.json")


def test_summary_golden_file_and_stdin_output_is_deterministic(monkeypatch):
    monkeypatch.chdir(REPO_ROOT)

    result = runner.invoke(
        app,
        ["summary", "tests/fixtures/golden/summary_stdin_file.log", "-", "--out", "-"],
        input="2025-01-01T00:00:01Z ERROR worker: from-stdin\n",
    )

    assert result.exit_code == 0
    assert result.stdout == _golden("summary_output_stdin.json")


def test_summary_golden_filter_miss_output_is_deterministic(monkeypatch):
    monkeypatch.chdir(REPO_ROOT)

    result = runner.invoke(
        app,
        ["summary", "tests/fixtures/golden/mixed_input.log", "--out", "-", "--component", "cache"],
    )

    assert result.exit_code == 0
    assert result.stdout == _golden("summary_output_filter_miss.json")


def test_summary_contract_alias_shaped_json_fixture_normalizes_components_and_evidence(monkeypatch):
    monkeypatch.chdir(REPO_ROOT)

    result = runner.invoke(app, ["summary", "tests/fixtures/golden/alias_shaped_input.log", "--out", "-"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload == {
        "schema_version": cli_module.SUMMARY_SCHEMA_VERSION,
        "incident_window": {
            "start": "2025-01-01T00:00:01+00:00",
            "end": "2025-01-01T00:00:03+00:00",
        },
        "event_count": 3,
        "error_count": 2,
        "top_components": [
            {"name": "api", "count": 1},
            {"name": "payments", "count": 1},
            {"name": "worker.queue", "count": 1},
        ],
        "top_error_signatures": [
            {"name": "job failed cid=<id>", "count": 1},
            {"name": "request failed cid=<id>", "count": 1},
        ],
        "evidence_by_source": [
            {"source": "tests/fixtures/golden/alias_shaped_input.log", "count": 2},
        ],
        "correlation_id_coverage": {
            "covered_events": 3,
            "total_events": 3,
            "coverage_ratio": 1.0,
        },
        "parse_summary": {
            "total_lines": 3,
            "parsed_lines": 3,
            "dropped_lines": 0,
            "drop_ratio": 0.0,
            "dropped_reasons": {},
        },
    }
