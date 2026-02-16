import json
from importlib.metadata import PackageNotFoundError, version as package_version

from typer.testing import CliRunner

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


def test_version_flag():
    result = runner.invoke(app, ["--version"])

    assert result.exit_code == 0
    assert result.stdout.strip() == _expected_version()
