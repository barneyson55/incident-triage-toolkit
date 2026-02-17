import json
from importlib.metadata import PackageNotFoundError, version as package_version

import pytest
from typer.testing import CliRunner

import triage_toolkit.cli as cli_module
from triage_toolkit import __version__
from triage_toolkit.cli import app

runner = CliRunner()


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
    assert payload["events"][0]["component"] == "api"
    assert payload["parse_summary"] == {
        "total_lines": 1,
        "parsed_lines": 1,
        "dropped_lines": 0,
        "drop_ratio": 0.0,
        "dropped_reasons": {},
    }


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


def test_timeline_strict_fails_when_no_parsed_lines(tmp_path):
    sample = tmp_path / "sample.log"
    sample.write_text("not a log line\n", encoding="utf-8")

    result = runner.invoke(app, ["timeline", str(sample), "--out", "-", "--strict"])

    assert result.exit_code == 2
    assert "Strict parse gate failed: parsed_lines == 0" in result.output


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


def test_parse_stdout_normalizes_offset_timestamp_to_utc(tmp_path):
    sample = tmp_path / "sample.log"
    sample.write_text("2025-01-01T02:00:01+02:00 INFO api: hello cid=c-1\n", encoding="utf-8")

    result = runner.invoke(app, ["parse", str(sample), "--out", "-"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["events"][0]["timestamp"] == "2025-01-01T00:00:01+00:00"


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
