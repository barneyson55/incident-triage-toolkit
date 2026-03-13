from __future__ import annotations

import os
import runpy
import subprocess
import sys
import sysconfig
from importlib.metadata import PackageNotFoundError, version as package_version
from pathlib import Path

from triage_toolkit import __version__


REPO_ROOT = Path(__file__).resolve().parents[1]


def _triage_console_script() -> str:
    scripts_dir = Path(sysconfig.get_path("scripts"))
    candidates = [scripts_dir / "triage"]
    if os.name == "nt":
        candidates.extend(
            [
                scripts_dir / "triage.exe",
                scripts_dir / "triage.cmd",
                scripts_dir / "triage.bat",
            ]
        )

    for candidate in candidates:
        if candidate.exists():
            return str(candidate)

    raise AssertionError(f"Installed triage console script not found in {scripts_dir}")


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


def test_installed_triage_console_script_version_reports_expected_value():
    result = subprocess.run(
        [_triage_console_script(), "--version"],
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


def test_installed_triage_console_script_parse_missing_file_surfaces_operator_error():
    result = subprocess.run(
        [_triage_console_script(), "parse", "missing-file.log", "--out", "-"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 2
    assert result.stdout == ""
    assert "Input file not found: missing-file.log" in result.stderr
