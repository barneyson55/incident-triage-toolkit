from __future__ import annotations

import runpy
import subprocess
import sys
from importlib.metadata import PackageNotFoundError, version as package_version
from pathlib import Path

from triage_toolkit import __version__


REPO_ROOT = Path(__file__).resolve().parents[1]


def _expected_version() -> str:
    try:
        return package_version("incident-triage-toolkit")
    except PackageNotFoundError:
        return __version__


def test_module_entrypoint_invokes_cli_main(monkeypatch):
    called = {"value": False}

    def fake_main() -> None:
        called["value"] = True

    monkeypatch.setattr("triage_toolkit.cli.main", fake_main)

    runpy.run_module("triage_toolkit.__main__", run_name="__main__")

    assert called["value"] is True



def test_python_dash_m_triage_toolkit_version_reports_expected_value():
    result = subprocess.run(
        [sys.executable, "-m", "triage_toolkit", "--version"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert result.stdout.strip() == _expected_version()
    assert result.stderr == ""



def test_python_dash_m_triage_toolkit_parse_missing_file_surfaces_operator_error():
    result = subprocess.run(
        [sys.executable, "-m", "triage_toolkit", "parse", "missing-file.log", "--out", "-"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 2
    assert result.stdout == ""
    assert "Input file not found: missing-file.log" in result.stderr
