from __future__ import annotations

import json
from collections import Counter
from importlib.metadata import PackageNotFoundError, version as package_version
from pathlib import Path
from typing import Any, NoReturn

import typer

from . import __version__
from .parser import parse_file, parse_file_with_summary
from .runbook import build_runbook
from .timeline import build_timeline

_PACKAGE_NAME = "incident-triage-toolkit"
PARSE_SCHEMA_VERSION = "1.0.0"
SUMMARY_SCHEMA_VERSION = "1.0.0"

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


def _merge_parse_summaries(summaries: list[dict[str, Any]]) -> dict[str, Any]:
    total_lines = sum(int(summary["total_lines"]) for summary in summaries)
    parsed_lines = sum(int(summary["parsed_lines"]) for summary in summaries)
    dropped_lines = total_lines - parsed_lines
    drop_ratio = dropped_lines / total_lines if total_lines else 0.0

    dropped_reasons: Counter[str] = Counter()
    for summary in summaries:
        for reason, count in summary.get("dropped_reasons", {}).items():
            dropped_reasons[reason] += int(count)

    return {
        "total_lines": total_lines,
        "parsed_lines": parsed_lines,
        "dropped_lines": dropped_lines,
        "drop_ratio": round(drop_ratio, 6),
        "dropped_reasons": {reason: dropped_reasons[reason] for reason in sorted(dropped_reasons)},
    }


def _read_events_for_parse(paths: list[Path]) -> tuple[list[Any], dict[str, Any]]:
    if not paths:
        _fail("At least one input file path is required.")

    merged_events: list[tuple[Any, int, int]] = []
    per_source: list[dict[str, Any]] = []

    for source_index, path in enumerate(paths):
        events, summary = _read_events_with_summary(path)
        merged_events.extend((event, source_index, event_index) for event_index, event in enumerate(events))
        per_source.append({"path": str(path), **summary})

    merged_events.sort(key=lambda item: (item[0].timestamp, item[1], item[2]))
    all_events = [item[0] for item in merged_events]

    aggregate = _merge_parse_summaries(per_source)
    if len(paths) > 1:
        aggregate["per_source"] = per_source
    return all_events, aggregate


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


def _top_items(counter: Counter[str], limit: int = 3) -> list[dict[str, Any]]:
    ordered = sorted(counter.items(), key=lambda item: (-item[1], item[0]))
    return [{"name": name, "count": count} for name, count in ordered[:limit]]


def _build_incident_summary(events: list[Any]) -> dict[str, Any]:
    event_count = len(events)
    start = events[0].timestamp.isoformat() if events else None
    end = events[-1].timestamp.isoformat() if events else None

    component_counts = Counter(event.component for event in events)
    error_events = [event for event in events if event.level.upper() == "ERROR"]
    error_signature_counts = Counter(event.message for event in error_events)

    correlated = sum(1 for event in events if event.correlation_id)
    correlation_coverage = 0.0 if event_count == 0 else correlated / event_count

    return {
        "schema_version": SUMMARY_SCHEMA_VERSION,
        "incident_window": {
            "start": start,
            "end": end,
        },
        "event_count": event_count,
        "error_count": len(error_events),
        "top_components": _top_items(component_counts),
        "top_error_signatures": _top_items(error_signature_counts),
        "correlation_id_coverage": {
            "covered_events": correlated,
            "total_events": event_count,
            "coverage_ratio": round(correlation_coverage, 6),
        },
    }


@app.command()
def parse(
    paths: list[Path] = typer.Argument(..., help="One or more input log files."),
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
    """Parse one or more log files and write normalized JSON output."""
    events, summary = _read_events_for_parse(paths)
    strict_error = _strict_parse_error(summary, max_drop_ratio) if strict else None
    if strict_error:
        _fail(strict_error)

    payload = {
        "schema_version": PARSE_SCHEMA_VERSION,
        "events": [event.to_dict() for event in events],
        "parse_summary": summary,
    }
    _write_output(out, json.dumps(payload, indent=2))
    if out != "-":
        typer.echo(f"Wrote {summary['parsed_lines']} events to {out}")


@app.command()
def summary(
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
    """Generate a machine-readable incident summary JSON output."""
    events, parse_summary = _read_events_with_summary(path)
    strict_error = _strict_parse_error(parse_summary, max_drop_ratio) if strict else None
    if strict_error:
        _fail(strict_error)

    payload = _build_incident_summary(events)
    payload["parse_summary"] = parse_summary
    _write_output(out, json.dumps(payload, indent=2))
    if out != "-":
        typer.echo(f"Wrote incident summary to {out}")


@app.command()
def timeline(
    paths: list[Path] = typer.Argument(..., help="One or more input log files."),
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
    """Generate a timeline markdown file from one or more log files."""
    events, summary = _read_events_for_parse(paths)
    strict_error = _strict_parse_error(summary, max_drop_ratio) if strict else None
    if strict_error:
        _fail(strict_error)

    content = build_timeline(events)
    _write_output(out, content)
    if out != "-":
        typer.echo(f"Wrote timeline to {out}")


@app.command()
def runbook(
    paths: list[Path] = typer.Argument(..., help="One or more input log files."),
    out: str = typer.Option(..., "--out", "-o", help="Output path or '-' for stdout."),
    title: str = typer.Option("Incident: Untitled", "--title"),
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
    """Generate a runbook skeleton from one or more log files."""
    events, summary = _read_events_for_parse(paths)
    strict_error = _strict_parse_error(summary, max_drop_ratio) if strict else None
    if strict_error:
        _fail(strict_error)

    content = build_runbook(events, title)
    _write_output(out, content)
    if out != "-":
        typer.echo(f"Wrote runbook to {out}")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
