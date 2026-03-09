import json
from importlib.metadata import PackageNotFoundError, version as package_version
from pathlib import Path

import pytest
from typer.testing import CliRunner

import triage_toolkit.cli as cli_module
from triage_toolkit import __version__
from triage_toolkit.cli import app

runner = CliRunner()
GOLDEN_DIR = Path(__file__).parent / "fixtures" / "golden"


def _expected_version() -> str:
    try:
        return package_version("incident-triage-toolkit")
    except PackageNotFoundError:
        return __version__


def test_parse_stdout(tmp_path):
    sample = tmp_path / "sample.log"
    sample.write_text("2025-01-01T00:00:01Z INFO api: hello cid=c-1\n", encoding="utf-8")

    result = runner.invoke(app, ["parse", str(sample), "--out", "-"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["schema_version"] == cli_module.PARSE_SCHEMA_VERSION
    assert payload["events"][0]["component"] == "api"
    assert payload["parse_summary"] == {
        "total_lines": 1,
        "parsed_lines": 1,
        "dropped_lines": 0,
        "drop_ratio": 0.0,
        "dropped_reasons": {},
    }


def test_parse_contract_required_top_level_keys_for_current_schema(tmp_path):
    sample = tmp_path / "sample.log"
    sample.write_text("2025-01-01T00:00:01Z INFO api: hello\n", encoding="utf-8")

    result = runner.invoke(app, ["parse", str(sample), "--out", "-"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["schema_version"] == cli_module.PARSE_SCHEMA_VERSION
    assert set(payload.keys()) == {"schema_version", "events", "parse_summary"}


def test_parse_golden_output_contract_is_deterministic():
    sample = GOLDEN_DIR / "mixed_input.log"
    expected = (GOLDEN_DIR / "parse_output.json").read_text(encoding="utf-8")

    result = runner.invoke(app, ["parse", str(sample), "--out", "-"])

    assert result.exit_code == 0
    assert result.stdout == expected


def test_parse_multiple_inputs_merges_in_deterministic_timestamp_order(tmp_path):
    source_a = tmp_path / "a.log"
    source_b = tmp_path / "b.log"
    source_a.write_text("2025-01-01T00:00:02Z INFO api: second\n", encoding="utf-8")
    source_b.write_text("2025-01-01T00:00:01Z INFO web: first\n", encoding="utf-8")

    result = runner.invoke(app, ["parse", str(source_a), str(source_b), "--out", "-"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert [event["component"] for event in payload["events"]] == ["web", "api"]
    assert payload["parse_summary"]["parsed_lines"] == 2
    assert [item["path"] for item in payload["parse_summary"]["per_source"]] == [
        str(source_a),
        str(source_b),
    ]


def test_parse_multiple_inputs_uses_stable_tiebreak_for_same_timestamp(tmp_path):
    source_a = tmp_path / "a.log"
    source_b = tmp_path / "b.log"
    source_a.write_text(
        "\n".join(
            [
                "2025-01-01T00:00:01Z INFO api: from-a-1",
                "2025-01-01T00:00:01Z INFO api: from-a-2",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    source_b.write_text("2025-01-01T00:00:01Z INFO db: from-b\n", encoding="utf-8")

    result = runner.invoke(app, ["parse", str(source_a), str(source_b), "--out", "-"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert [(event["component"], event["message"]) for event in payload["events"]] == [
        ("api", "from-a-1"),
        ("api", "from-a-2"),
        ("db", "from-b"),
    ]


def test_parse_multiple_inputs_per_source_summary_keeps_source_order_and_reason_counts(tmp_path):
    source_a = tmp_path / "a.log"
    source_b = tmp_path / "b.log"
    source_a.write_text("bad-a\n", encoding="utf-8")
    source_b.write_text("2025-01-01T00:00:01Z INFO web: ok\nbad-b\n", encoding="utf-8")

    result = runner.invoke(app, ["parse", str(source_a), str(source_b), "--out", "-"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["parse_summary"]["dropped_reasons"] == {"unrecognized_text": 2}
    assert payload["parse_summary"]["per_source"] == [
        {
            "path": str(source_a),
            "total_lines": 1,
            "parsed_lines": 0,
            "dropped_lines": 1,
            "drop_ratio": 1.0,
            "dropped_reasons": {"unrecognized_text": 1},
        },
        {
            "path": str(source_b),
            "total_lines": 2,
            "parsed_lines": 1,
            "dropped_lines": 1,
            "drop_ratio": 0.5,
            "dropped_reasons": {"unrecognized_text": 1},
        },
    ]



def test_parse_stdout_with_dropped_examples_respects_diagnostics_limit(tmp_path):
    sample = tmp_path / "sample.log"
    sample.write_text(
        "\n".join(
            [
                "bad-a",
                '{"timestamp":"bad-ts","message":"broken"}',
                "2025-01-01T00:00:01Z INFO api: ok",
                '{"message":"missing timestamp"}',
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    result = runner.invoke(
        app,
        ["parse", str(sample), "--out", "-", "--diagnostics-limit", "2"],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["schema_version"] == cli_module.PARSE_SCHEMA_VERSION
    assert payload["parse_summary"]["dropped_line_diagnostics"] == [
        {
            "source_path": str(sample),
            "line_number": 1,
            "reason": "unrecognized_text",
            "raw_line": "bad-a",
        },
        {
            "source_path": str(sample),
            "line_number": 2,
            "reason": "invalid_timestamp",
            "raw_line": '{"timestamp":"bad-ts","message":"broken"}',
        },
    ]



def test_parse_multiple_inputs_dropped_examples_follow_cli_input_order(tmp_path):
    source_a = tmp_path / "a.log"
    source_b = tmp_path / "b.log"
    source_a.write_text("bad-a-1\nbad-a-2\n", encoding="utf-8")
    source_b.write_text("bad-b-1\n", encoding="utf-8")

    result = runner.invoke(
        app,
        [
            "parse",
            str(source_a),
            str(source_b),
            "--out",
            "-",
            "--diagnostics-limit",
            "2",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["parse_summary"]["dropped_line_diagnostics"] == [
        {
            "source_path": str(source_a),
            "line_number": 1,
            "reason": "unrecognized_text",
            "raw_line": "bad-a-1",
        },
        {
            "source_path": str(source_a),
            "line_number": 2,
            "reason": "unrecognized_text",
            "raw_line": "bad-a-2",
        },
    ]
    assert all(
        "dropped_line_diagnostics" not in source_summary
        for source_summary in payload["parse_summary"]["per_source"]
    )


def test_parse_stdin_only_uses_stable_source_label_for_diagnostics():
    result = runner.invoke(
        app,
        ["parse", "-", "--out", "-", "--diagnostics-limit", "1"],
        input="bad-line\n2025-01-01T00:00:01Z INFO api: ok cid=c-1\n",
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["events"][0]["component"] == "api"
    assert payload["parse_summary"]["dropped_line_diagnostics"] == [
        {
            "source_path": "-",
            "line_number": 1,
            "reason": "unrecognized_text",
            "raw_line": "bad-line",
        }
    ]


def test_parse_multiple_inputs_with_stdin_preserve_cli_input_order_for_tied_timestamps(tmp_path):
    source_file = tmp_path / "file.log"
    source_file.write_text("2025-01-01T00:00:01Z INFO api: from-file\n", encoding="utf-8")

    result = runner.invoke(
        app,
        ["parse", str(source_file), "-", "--out", "-"],
        input="2025-01-01T00:00:01Z INFO web: from-stdin\n",
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert [(event["component"], event["message"]) for event in payload["events"]] == [
        ("api", "from-file"),
        ("web", "from-stdin"),
    ]
    assert [item["path"] for item in payload["parse_summary"]["per_source"]] == [
        str(source_file),
        "-",
    ]


def test_parse_rejects_duplicate_stdin_sources():
    result = runner.invoke(app, ["parse", "-", "-", "--out", "-"])

    assert result.exit_code == 2
    assert "Standard input source '-' may be specified at most once." in result.output


def test_parse_strict_with_stdin_uses_raw_ingestion_quality():
    result = runner.invoke(
        app,
        ["parse", "-", "--out", "-", "--strict", "--max-drop-ratio", "0.49"],
        input="2025-01-01T00:00:01Z INFO api: ok\nbad-line\n",
    )

    assert result.exit_code == 2
    assert "drop_ratio=0.500000 exceeds max_drop_ratio=0.490000" in result.output


def test_summary_accepts_stdin_only():
    result = runner.invoke(
        app,
        ["summary", "-", "--out", "-"],
        input="2025-01-01T00:00:01Z ERROR api: failed cid=c-1\n",
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["event_count"] == 1
    assert payload["error_count"] == 1
    assert payload["top_components"] == [{"name": "api", "count": 1}]


def test_timeline_accepts_stdin_only():
    result = runner.invoke(
        app,
        ["timeline", "-", "--out", "-"],
        input="2025-01-01T00:00:01Z INFO api: ok cid=c-1\n",
    )

    assert result.exit_code == 0
    assert "| 2025-01-01T00:00:01+00:00 | INFO | api | ok cid=c-1 |" in result.stdout


def test_runbook_accepts_stdin_only():
    result = runner.invoke(
        app,
        ["runbook", "-", "--out", "-", "--title", "Incident: STDIN"],
        input="2025-01-01T00:00:01Z ERROR api: failed cid=c-1\n",
    )

    assert result.exit_code == 0
    assert result.stdout.startswith("# Incident: STDIN\n")
    assert "- Error events: 1 of 1 total" in result.stdout


def test_parse_missing_file_error():
    result = runner.invoke(app, ["parse", "missing-file.log", "--out", "-"])

    assert result.exit_code == 2
    assert "Input file not found: missing-file.log" in result.output


def test_parse_directory_input_error(tmp_path):
    input_dir = tmp_path / "logs"
    input_dir.mkdir()

    result = runner.invoke(app, ["parse", str(input_dir), "--out", "-"])

    assert result.exit_code == 2
    assert f"Input path is a directory, expected a file: {input_dir}" in result.output


def test_parse_utf8_decode_error(tmp_path):
    sample = tmp_path / "bad.log"
    sample.write_bytes(b"\xff\xfe\xfa")

    result = runner.invoke(app, ["parse", str(sample), "--out", "-"])

    assert result.exit_code == 2
    assert f"Input file is not valid UTF-8 text: {sample}" in result.output


def test_parse_permission_error(monkeypatch, tmp_path):
    sample = tmp_path / "sample.log"

    def _raise_permission(_path):
        raise PermissionError("denied")

    monkeypatch.setattr(cli_module, "parse_file_with_summary", _raise_permission)

    result = runner.invoke(app, ["parse", str(sample), "--out", "-"])

    assert result.exit_code == 2
    assert f"Input file is not readable: {sample}" in result.output


def test_parse_generic_read_os_error(monkeypatch, tmp_path):
    sample = tmp_path / "sample.log"

    def _raise_os_error(_path):
        raise OSError("i/o exploded")

    monkeypatch.setattr(cli_module, "parse_file_with_summary", _raise_os_error)

    result = runner.invoke(app, ["parse", str(sample), "--out", "-"])

    assert result.exit_code == 2
    assert f"Could not read input file '{sample}': i/o exploded" in result.output


def test_parse_strict_fails_when_no_parsed_lines(tmp_path):
    sample = tmp_path / "sample.log"
    sample.write_text("not a log line\n", encoding="utf-8")

    result = runner.invoke(app, ["parse", str(sample), "--out", "-", "--strict"])

    assert result.exit_code == 2
    assert "Strict parse gate failed: parsed_lines == 0" in result.output


def test_parse_strict_fails_when_drop_ratio_exceeds_threshold(tmp_path):
    sample = tmp_path / "sample.log"
    sample.write_text(
        "\n".join(
            [
                "2025-01-01T00:00:01Z INFO api: ok",
                "not a log line",
            ]
        ),
        encoding="utf-8",
    )

    result = runner.invoke(
        app,
        [
            "parse",
            str(sample),
            "--out",
            "-",
            "--strict",
            "--max-drop-ratio",
            "0.25",
        ],
    )

    assert result.exit_code == 2
    assert "drop_ratio=0.500000 exceeds max_drop_ratio=0.250000" in result.output


def test_parse_strict_accepts_drop_ratio_within_limit(tmp_path):
    sample = tmp_path / "sample.log"
    sample.write_text(
        "\n".join(
            [
                "2025-01-01T00:00:01Z INFO api: ok",
                "not a log line",
            ]
        ),
        encoding="utf-8",
    )

    result = runner.invoke(
        app,
        [
            "parse",
            str(sample),
            "--out",
            "-",
            "--strict",
            "--max-drop-ratio",
            "0.5",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["parse_summary"]["drop_ratio"] == 0.5


def test_parse_strict_stream_large_input_fails_when_drop_ratio_exceeds_threshold(tmp_path):
    sample = tmp_path / "large.log"
    valid_line = "2025-01-01T00:00:01Z INFO api: ok\n"
    invalid_line = "not a log line\n"

    with sample.open("w", encoding="utf-8") as handle:
        for _ in range(2_000):
            handle.write(valid_line)
            handle.write(invalid_line)

    result = runner.invoke(
        app,
        [
            "parse",
            str(sample),
            "--out",
            "-",
            "--strict",
            "--max-drop-ratio",
            "0.49",
        ],
    )

    assert result.exit_code == 2
    assert "drop_ratio=0.500000 exceeds max_drop_ratio=0.490000" in result.output


def test_summary_stdout_returns_machine_readable_contract(tmp_path):
    sample = tmp_path / "sample.log"
    sample.write_text(
        "\n".join(
            [
                "2025-01-01T00:00:01Z INFO api: request accepted cid=c-1",
                "2025-01-01T00:00:02Z ERROR db: connection timeout cid=c-2",
                "2025-01-01T00:00:03Z ERROR db: connection timeout",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    result = runner.invoke(app, ["summary", str(sample), "--out", "-"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["schema_version"] == cli_module.SUMMARY_SCHEMA_VERSION
    assert payload["incident_window"] == {
        "start": "2025-01-01T00:00:01+00:00",
        "end": "2025-01-01T00:00:03+00:00",
    }
    assert payload["event_count"] == 3
    assert payload["error_count"] == 2
    assert payload["top_components"][0] == {"name": "db", "count": 2}
    assert payload["top_error_signatures"][0] == {"name": "connection timeout", "count": 1}
    assert payload["correlation_id_coverage"] == {
        "covered_events": 2,
        "total_events": 3,
        "coverage_ratio": 0.666667,
    }
    assert "per_source" not in payload["parse_summary"]


def test_summary_multiple_inputs_merges_counts_and_incident_window(tmp_path):
    source_a = tmp_path / "a.log"
    source_b = tmp_path / "b.log"
    source_a.write_text(
        "\n".join(
            [
                "2025-01-01T00:00:03Z ERROR db: connection timeout",
                "bad-a",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    source_b.write_text(
        "\n".join(
            [
                "2025-01-01T00:00:01Z INFO api: request accepted cid=c-1",
                "2025-01-01T00:00:02Z ERROR web: connection timeout",
                "bad-b",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    result = runner.invoke(app, ["summary", str(source_a), str(source_b), "--out", "-"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["incident_window"] == {
        "start": "2025-01-01T00:00:01+00:00",
        "end": "2025-01-01T00:00:03+00:00",
    }
    assert payload["event_count"] == 3
    assert payload["error_count"] == 2
    assert payload["top_components"] == [
        {"name": "api", "count": 1},
        {"name": "db", "count": 1},
        {"name": "web", "count": 1},
    ]
    assert payload["top_error_signatures"] == [{"name": "connection timeout", "count": 2}]
    assert payload["correlation_id_coverage"] == {
        "covered_events": 1,
        "total_events": 3,
        "coverage_ratio": 0.333333,
    }
    assert payload["parse_summary"] == {
        "total_lines": 5,
        "parsed_lines": 3,
        "dropped_lines": 2,
        "drop_ratio": 0.4,
        "dropped_reasons": {"unrecognized_text": 2},
        "per_source": [
            {
                "path": str(source_a),
                "total_lines": 2,
                "parsed_lines": 1,
                "dropped_lines": 1,
                "drop_ratio": 0.5,
                "dropped_reasons": {"unrecognized_text": 1},
            },
            {
                "path": str(source_b),
                "total_lines": 3,
                "parsed_lines": 2,
                "dropped_lines": 1,
                "drop_ratio": 0.333333,
                "dropped_reasons": {"unrecognized_text": 1},
            },
        ],
    }


def test_summary_multiple_inputs_strict_uses_aggregate_drop_ratio(tmp_path):
    source_a = tmp_path / "a.log"
    source_b = tmp_path / "b.log"
    source_a.write_text("2025-01-01T00:00:01Z INFO api: ok\n", encoding="utf-8")
    source_b.write_text("bad-b\n", encoding="utf-8")

    result = runner.invoke(
        app,
        [
            "summary",
            str(source_a),
            str(source_b),
            "--out",
            "-",
            "--strict",
            "--max-drop-ratio",
            "0.49",
        ],
    )

    assert result.exit_code == 2
    assert "drop_ratio=0.500000 exceeds max_drop_ratio=0.490000" in result.output


def test_summary_strict_fails_when_no_parsed_lines(tmp_path):
    sample = tmp_path / "sample.log"
    sample.write_text("not a log line\n", encoding="utf-8")

    result = runner.invoke(app, ["summary", str(sample), "--out", "-", "--strict"])

    assert result.exit_code == 2
    assert "Strict parse gate failed: parsed_lines == 0" in result.output


def test_summary_top_lists_are_deterministic_for_tied_counts(tmp_path):
    sample = tmp_path / "sample.log"
    sample.write_text(
        "\n".join(
            [
                "2025-01-01T00:00:01Z INFO web: accepted",
                "2025-01-01T00:00:02Z INFO api: accepted",
                "2025-01-01T00:00:03Z ERROR db: timeout",
                "2025-01-01T00:00:04Z ERROR cache: timeout",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    result = runner.invoke(app, ["summary", str(sample), "--out", "-"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["top_components"] == [
        {"name": "api", "count": 1},
        {"name": "cache", "count": 1},
        {"name": "db", "count": 1},
    ]
    assert payload["top_error_signatures"] == [
        {"name": "timeout", "count": 2},
    ]


def test_summary_filters_slice_events_with_repeated_or_flags_and_and_across_fields(tmp_path):
    sample = tmp_path / "sample.log"
    sample.write_text(
        "\n".join(
            [
                "2025-01-01T00:00:01Z INFO api: accepted cid=c-1",
                "2025-01-01T00:00:02Z ERROR api: timeout cid=c-2",
                "2025-01-01T00:00:03Z ERROR worker: timeout cid=c-2",
                "2025-01-01T00:00:04Z ERROR web: timeout cid=c-3",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    result = runner.invoke(
        app,
        [
            "summary",
            str(sample),
            "--out",
            "-",
            "--component",
            "api",
            "--component",
            "worker",
            "--level",
            "error",
            "--correlation-id",
            "c-2",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["incident_window"] == {
        "start": "2025-01-01T00:00:02+00:00",
        "end": "2025-01-01T00:00:03+00:00",
    }
    assert payload["event_count"] == 2
    assert payload["error_count"] == 2
    assert payload["top_components"] == [
        {"name": "api", "count": 1},
        {"name": "worker", "count": 1},
    ]
    assert payload["top_error_signatures"] == [{"name": "timeout cid=c-2", "count": 2}]
    assert payload["correlation_id_coverage"] == {
        "covered_events": 2,
        "total_events": 2,
        "coverage_ratio": 1.0,
    }
    assert payload["parse_summary"] == {
        "total_lines": 4,
        "parsed_lines": 4,
        "dropped_lines": 0,
        "drop_ratio": 0.0,
        "dropped_reasons": {},
    }


def test_summary_filters_return_empty_slice_without_mutating_raw_parse_summary(tmp_path):
    sample = tmp_path / "sample.log"
    sample.write_text(
        "2025-01-01T00:00:01Z INFO api: accepted cid=c-1\n",
        encoding="utf-8",
    )

    result = runner.invoke(
        app,
        ["summary", str(sample), "--out", "-", "--component", "worker"],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["incident_window"] == {"start": None, "end": None}
    assert payload["event_count"] == 0
    assert payload["error_count"] == 0
    assert payload["top_components"] == []
    assert payload["top_error_signatures"] == []
    assert payload["correlation_id_coverage"] == {
        "covered_events": 0,
        "total_events": 0,
        "coverage_ratio": 0.0,
    }
    assert payload["parse_summary"] == {
        "total_lines": 1,
        "parsed_lines": 1,
        "dropped_lines": 0,
        "drop_ratio": 0.0,
        "dropped_reasons": {},
    }


def test_summary_filters_do_not_bypass_strict_parse_gate_on_raw_ingestion(tmp_path):
    sample = tmp_path / "sample.log"
    sample.write_text(
        "2025-01-01T00:00:01Z INFO api: accepted cid=c-1\nbad-line\n",
        encoding="utf-8",
    )

    result = runner.invoke(
        app,
        [
            "summary",
            str(sample),
            "--out",
            "-",
            "--component",
            "api",
            "--strict",
            "--max-drop-ratio",
            "0.49",
        ],
    )

    assert result.exit_code == 2
    assert "drop_ratio=0.500000 exceeds max_drop_ratio=0.490000" in result.output


def test_timeline_strict_fails_when_no_parsed_lines(tmp_path):
    sample = tmp_path / "sample.log"
    sample.write_text("not a log line\n", encoding="utf-8")

    result = runner.invoke(app, ["timeline", str(sample), "--out", "-", "--strict"])

    assert result.exit_code == 2
    assert "Strict parse gate failed: parsed_lines == 0" in result.output


def test_timeline_multiple_inputs_merge_in_deterministic_order(tmp_path):
    source_a = tmp_path / "a.log"
    source_b = tmp_path / "b.log"
    source_a.write_text("2025-01-01T00:00:02Z INFO api: from-a\n", encoding="utf-8")
    source_b.write_text("2025-01-01T00:00:01Z INFO db: from-b\n", encoding="utf-8")

    result = runner.invoke(app, ["timeline", str(source_a), str(source_b), "--out", "-"])

    assert result.exit_code == 0
    first = result.stdout.find("2025-01-01T00:00:01+00:00")
    second = result.stdout.find("2025-01-01T00:00:02+00:00")
    assert first != -1 and second != -1 and first < second


def test_timeline_filters_slice_events_with_repeated_or_flags_and_preserve_order(tmp_path):
    sample = tmp_path / "sample.log"
    sample.write_text(
        "\n".join(
            [
                "2025-01-01T00:00:01Z INFO api: accepted cid=c-1",
                "2025-01-01T00:00:02Z ERROR worker: timeout cid=c-2",
                "2025-01-01T00:00:02Z ERROR api: timeout cid=c-2",
                "2025-01-01T00:00:03Z ERROR web: timeout cid=c-3",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    result = runner.invoke(
        app,
        [
            "timeline",
            str(sample),
            "--out",
            "-",
            "--component",
            "worker",
            "--component",
            "api",
            "--level",
            "ERROR",
            "--correlation-id",
            "c-2",
        ],
    )

    assert result.exit_code == 0
    assert "accepted cid=c-1" not in result.stdout
    assert "web" not in result.stdout
    worker_index = result.stdout.find("| 2025-01-01T00:00:02+00:00 | ERROR | worker | timeout cid=c-2 |")
    api_index = result.stdout.find("| 2025-01-01T00:00:02+00:00 | ERROR | api | timeout cid=c-2 |")
    assert 0 <= worker_index < api_index


def test_timeline_filters_do_not_bypass_strict_parse_gate_on_raw_ingestion(tmp_path):
    sample = tmp_path / "sample.log"
    sample.write_text(
        "2025-01-01T00:00:01Z INFO api: accepted cid=c-1\nbad-line\n",
        encoding="utf-8",
    )

    result = runner.invoke(
        app,
        [
            "timeline",
            str(sample),
            "--out",
            "-",
            "--component",
            "api",
            "--strict",
            "--max-drop-ratio",
            "0.49",
        ],
    )

    assert result.exit_code == 2
    assert "drop_ratio=0.500000 exceeds max_drop_ratio=0.490000" in result.output


def test_runbook_filters_slice_events_with_repeated_or_flags_and_and_across_fields(tmp_path):
    sample = tmp_path / "sample.log"
    sample.write_text(
        "\n".join(
            [
                "2025-01-01T00:00:01Z INFO api: accepted cid=c-1",
                "2025-01-01T00:00:02Z ERROR api: timeout cid=c-2",
                "2025-01-01T00:00:03Z ERROR worker: timeout cid=c-2",
                "2025-01-01T00:00:04Z ERROR web: timeout cid=c-3",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    result = runner.invoke(
        app,
        [
            "runbook",
            str(sample),
            "--out",
            "-",
            "--title",
            "Incident: Filtered",
            "--component",
            "api",
            "--component",
            "worker",
            "--level",
            "error",
            "--correlation-id",
            "c-2",
        ],
    )

    assert result.exit_code == 0
    assert result.stdout.startswith("# Incident: Filtered\n")
    assert "- First observed: `2025-01-01T00:00:02+00:00`" in result.stdout
    assert "- Error events: 2 of 2 total" in result.stdout
    assert "- Suspected components: api, worker" in result.stdout


def test_runbook_filters_do_not_bypass_strict_parse_gate_on_raw_ingestion(tmp_path):
    sample = tmp_path / "sample.log"
    sample.write_text(
        "2025-01-01T00:00:01Z INFO api: accepted cid=c-1\nbad-line\n",
        encoding="utf-8",
    )

    result = runner.invoke(
        app,
        [
            "runbook",
            str(sample),
            "--out",
            "-",
            "--component",
            "api",
            "--strict",
            "--max-drop-ratio",
            "0.49",
        ],
    )

    assert result.exit_code == 2
    assert "drop_ratio=0.500000 exceeds max_drop_ratio=0.490000" in result.output


def test_runbook_strict_fails_when_drop_ratio_exceeds_threshold(tmp_path):
    sample = tmp_path / "sample.log"
    sample.write_text(
        "\n".join(
            [
                "2025-01-01T00:00:01Z INFO api: ok",
                "not a log line",
            ]
        ),
        encoding="utf-8",
    )

    result = runner.invoke(
        app,
        [
            "runbook",
            str(sample),
            "--out",
            "-",
            "--strict",
            "--max-drop-ratio",
            "0.25",
        ],
    )

    assert result.exit_code == 2
    assert "drop_ratio=0.500000 exceeds max_drop_ratio=0.250000" in result.output


def test_timeline_drop_ratio_strict_accepts_threshold(tmp_path):
    sample = tmp_path / "sample.log"
    sample.write_text(
        "\n".join(
            [
                "2025-01-01T00:00:01Z INFO api: ok",
                "not a log line",
            ]
        ),
        encoding="utf-8",
    )

    result = runner.invoke(
        app,
        [
            "timeline",
            str(sample),
            "--out",
            "-",
            "--strict",
            "--max-drop-ratio",
            "0.5",
        ],
    )

    assert result.exit_code == 0
    assert "# Incident Timeline" in result.stdout


def test_runbook_drop_ratio_strict_accepts_threshold(tmp_path):
    sample = tmp_path / "sample.log"
    sample.write_text(
        "\n".join(
            [
                "2025-01-01T00:00:01Z INFO api: ok",
                "not a log line",
            ]
        ),
        encoding="utf-8",
    )

    result = runner.invoke(
        app,
        [
            "runbook",
            str(sample),
            "--out",
            "-",
            "--strict",
            "--max-drop-ratio",
            "0.5",
        ],
    )

    assert result.exit_code == 0
    assert "# Incident: Untitled" in result.stdout


def test_runbook_multiple_inputs_include_earliest_observed_timestamp(tmp_path):
    source_a = tmp_path / "a.log"
    source_b = tmp_path / "b.log"
    source_a.write_text("2025-01-01T00:00:03Z INFO api: from-a\n", encoding="utf-8")
    source_b.write_text("2025-01-01T00:00:01Z ERROR db: from-b\n", encoding="utf-8")

    result = runner.invoke(app, ["runbook", str(source_a), str(source_b), "--out", "-"])

    assert result.exit_code == 0
    assert "- First observed: `2025-01-01T00:00:01+00:00`" in result.stdout


def test_parse_stdout_normalizes_offset_timestamp_to_utc_and_preserves_provenance(tmp_path):
    sample = tmp_path / "sample.log"
    sample.write_text("2025-01-01T02:00:01+02:00 INFO api: hello cid=c-1\n", encoding="utf-8")

    result = runner.invoke(app, ["parse", str(sample), "--out", "-"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    event = payload["events"][0]
    assert event["timestamp"] == "2025-01-01T00:00:01+00:00"
    assert event["source_timestamp"] == "2025-01-01T02:00:01+02:00"
    assert event["source_offset"] == "+02:00"


def test_parse_json_provenance_keeps_timezone_source_offset(tmp_path):
    sample = tmp_path / "sample.log"
    sample.write_text(
        '{"timestamp":"2024-12-31T19:00:01-05:00","component":"api","message":"hello"}\n',
        encoding="utf-8",
    )

    result = runner.invoke(app, ["parse", str(sample), "--out", "-"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    event = payload["events"][0]
    assert event["timestamp"] == "2025-01-01T00:00:01+00:00"
    assert event["source_timestamp"] == "2024-12-31T19:00:01-05:00"
    assert event["source_offset"] == "-05:00"


def test_parse_writes_output_file_and_reports_success(tmp_path):
    sample = tmp_path / "sample.log"
    sample.write_text("2025-01-01T00:00:01Z INFO api: hello\n", encoding="utf-8")
    output = tmp_path / "parsed.json"

    result = runner.invoke(app, ["parse", str(sample), "--out", str(output)])

    assert result.exit_code == 0
    assert f"Wrote 1 events to {output}" in result.output
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["parse_summary"]["parsed_lines"] == 1


def test_parse_fails_when_output_target_is_directory(tmp_path):
    sample = tmp_path / "sample.log"
    sample.write_text("2025-01-01T00:00:01Z INFO api: hello\n", encoding="utf-8")
    output_dir = tmp_path / "already-a-dir"
    output_dir.mkdir()

    result = runner.invoke(app, ["parse", str(sample), "--out", str(output_dir)])

    assert result.exit_code == 2
    assert f"Could not write output file '{output_dir}'" in result.output


def test_timeline_writes_output_file_and_reports_success(tmp_path):
    sample = tmp_path / "sample.log"
    sample.write_text("2025-01-01T00:00:01Z INFO api: hello\n", encoding="utf-8")
    output = tmp_path / "timeline.md"

    result = runner.invoke(app, ["timeline", str(sample), "--out", str(output)])

    assert result.exit_code == 0
    assert f"Wrote timeline to {output}" in result.output
    assert output.exists()


def test_runbook_writes_output_file_and_reports_success(tmp_path):
    sample = tmp_path / "sample.log"
    sample.write_text("2025-01-01T00:00:01Z INFO api: hello\n", encoding="utf-8")
    output = tmp_path / "runbook.md"

    result = runner.invoke(app, ["runbook", str(sample), "--out", str(output)])

    assert result.exit_code == 0
    assert f"Wrote runbook to {output}" in result.output
    assert output.exists()


def test_drop_ratio_zero_total_lines():
    assert cli_module._drop_ratio({"total_lines": 0, "dropped_lines": 3}) == 0.0


def test_read_events_maps_parse_errors(monkeypatch, tmp_path):
    sample = tmp_path / "sample.log"
    sample.write_text("x\n", encoding="utf-8")

    def _fail_with_runtime_error(message: str):
        raise RuntimeError(message)

    monkeypatch.setattr(cli_module, "_fail", _fail_with_runtime_error)

    cases = [
        (FileNotFoundError(), f"Input file not found: {sample}"),
        (PermissionError(), f"Input file is not readable: {sample}"),
        (IsADirectoryError(), f"Input path is a directory, expected a file: {sample}"),
        (
            UnicodeDecodeError("utf-8", b"\xff", 0, 1, "invalid start byte"),
            f"Input file is not valid UTF-8 text: {sample}",
        ),
        (OSError("disk failure"), f"Could not read input file '{sample}': disk failure"),
    ]

    for error, expected in cases:

        def _raise(_path, error=error):
            raise error

        monkeypatch.setattr(cli_module, "parse_file", _raise)

        with pytest.raises(RuntimeError) as exc_info:
            cli_module._read_events(sample)

        assert expected in str(exc_info.value)


def test_read_events_returns_parse_file_payload(monkeypatch, tmp_path):
    sample = tmp_path / "sample.log"
    sample.write_text("x\n", encoding="utf-8")

    events = ["parsed-event"]
    monkeypatch.setattr(cli_module, "parse_file", lambda _path: events)

    assert cli_module._read_events(sample) == events


def test_get_version_falls_back_to_module_version(monkeypatch):
    def _raise_package_not_found(_package_name: str) -> str:
        raise PackageNotFoundError

    monkeypatch.setattr(cli_module, "package_version", _raise_package_not_found)

    assert cli_module._get_version() == __version__


def test_version_flag():
    result = runner.invoke(app, ["--version"])

    assert result.exit_code == 0
    assert result.stdout.strip() == _expected_version()
