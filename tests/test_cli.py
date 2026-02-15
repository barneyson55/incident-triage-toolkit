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
    assert len(payload) == 1
    assert payload[0]["component"] == "api"


def test_parse_missing_file_error():
    result = runner.invoke(app, ["parse", "missing-file.log", "--out", "-"])

    assert result.exit_code == 2
    assert "Input file not found: missing-file.log" in result.output


def test_version_flag():
    result = runner.invoke(app, ["--version"])

    assert result.exit_code == 0
    assert result.stdout.strip() == _expected_version()
