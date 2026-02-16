from __future__ import annotations

import json
from importlib.metadata import PackageNotFoundError, version as package_version
from pathlib import Path
from typing import Any, NoReturn

import typer

from . import __version__
from .parser import parse_file, parse_file_with_summary
from .runbook import build_runbook
from .timeline import build_timeline

_PACKAGE_NAME = "incident-triage-toolkit"

app = typer.Typer(name="triage", help="Incident triage toolkit.")


def _get_version() -> str:
    try:
        return package_version(_PACKAGE_NAME)
    except PackageNotFoundError:
        return __version__


def _version_callback(value: bool | None) -> None:
    if value:
        typer.echo(_get_version())
        raise typer.Exit()


@app.callback()
def app_callback(
    version: bool | None = typer.Option(
        None,
        "--version",
        callback=_version_callback,
        is_eager=True,
        help="Show package version and exit.",
    ),
) -> None:
    """Incident triage toolkit."""


def _fail(message: str) -> NoReturn:
    typer.secho(f"Error: {message}", fg=typer.colors.RED, err=True)
    raise typer.Exit(code=2)


def _read_events(path: Path):
    try:
        return parse_file(path)
    except FileNotFoundError:
        _fail(f"Input file not found: {path}")
    except PermissionError:
        _fail(f"Input file is not readable: {path}")
    except IsADirectoryError:
        _fail(f"Input path is a directory, expected a file: {path}")
    except UnicodeDecodeError:
        _fail(f"Input file is not valid UTF-8 text: {path}")
    except OSError as exc:
        _fail(f"Could not read input file '{path}': {exc}")


def _read_events_with_summary(path: Path) -> tuple[list[Any], dict[str, Any]]:
    try:
        return parse_file_with_summary(path)
    except FileNotFoundError:
        _fail(f"Input file not found: {path}")
    except PermissionError:
        _fail(f"Input file is not readable: {path}")
    except IsADirectoryError:
        _fail(f"Input path is a directory, expected a file: {path}")
    except UnicodeDecodeError:
        _fail(f"Input file is not valid UTF-8 text: {path}")
    except OSError as exc:
        _fail(f"Could not read input file '{path}': {exc}")


def _write_output(target: str, content: str) -> None:
    if target == "-":
        typer.echo(content, nl=False)
        return

    path = Path(target)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    except OSError as exc:
        _fail(f"Could not write output file '{path}': {exc}")


def _drop_ratio(summary: dict[str, Any]) -> float:
    total_lines = int(summary["total_lines"])
    dropped_lines = int(summary["dropped_lines"])
    if total_lines == 0:
        return 0.0
    return dropped_lines / total_lines


def _strict_parse_error(summary: dict[str, Any], max_drop_ratio: float) -> str | None:
    if int(summary["parsed_lines"]) == 0:
        return f"Strict parse gate failed: parsed_lines == 0 (summary={json.dumps(summary, sort_keys=True)})"

    drop_ratio = _drop_ratio(summary)
    if drop_ratio > max_drop_ratio:
        return (
            "Strict parse gate failed: "
            f"drop_ratio={drop_ratio:.6f} exceeds max_drop_ratio={max_drop_ratio:.6f} "
            f"(summary={json.dumps(summary, sort_keys=True)})"
        )
    return None


@app.command()
def parse(
    path: Path,
    out: str = typer.Option(..., "--out", "-o", help="Output path or '-' for stdout."),
    strict: bool = typer.Option(
        False,
        "--strict",
        help="Fail with non-zero exit code when parse quality gates are violated.",
    ),
    max_drop_ratio: float = typer.Option(
        1.0,
        "--max-drop-ratio",
        min=0.0,
        max=1.0,
        help="Maximum allowed dropped/total line ratio in strict mode (0.0-1.0).",
    ),
) -> None:
    """Parse a log file and write normalized JSON output."""
    events, summary = _read_events_with_summary(path)
    strict_error = _strict_parse_error(summary, max_drop_ratio) if strict else None
    if strict_error:
        _fail(strict_error)

    payload = {
        "events": [event.to_dict() for event in events],
        "parse_summary": summary,
    }
    _write_output(out, json.dumps(payload, indent=2))
    if out != "-":
        typer.echo(f"Wrote {summary['parsed_lines']} events to {out}")


@app.command()
def timeline(
    path: Path,
    out: str = typer.Option(..., "--out", "-o", help="Output path or '-' for stdout."),
) -> None:
    """Generate a timeline markdown file from logs."""
    events = _read_events(path)
    content = build_timeline(events)
    _write_output(out, content)
    if out != "-":
        typer.echo(f"Wrote timeline to {out}")


@app.command()
def runbook(
    path: Path,
    out: str = typer.Option(..., "--out", "-o", help="Output path or '-' for stdout."),
    title: str = typer.Option("Incident: Untitled", "--title"),
) -> None:
    """Generate a runbook skeleton from logs."""
    events = _read_events(path)
    content = build_runbook(events, title)
    _write_output(out, content)
    if out != "-":
        typer.echo(f"Wrote runbook to {out}")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
