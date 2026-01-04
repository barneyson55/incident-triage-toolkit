from __future__ import annotations

import json
from pathlib import Path

import typer

from .parser import parse_file
from .runbook import build_runbook
from .timeline import build_timeline

app = typer.Typer(name="triage", help="Incident triage toolkit.")


def _write_output(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


@app.command()
def parse(path: Path, out: Path = typer.Option(..., "--out", "-o")) -> None:
    """Parse a log file and write normalized JSON output."""
    events = parse_file(path)
    payload = [event.to_dict() for event in events]
    _write_output(out, json.dumps(payload, indent=2))
    typer.echo(f"Wrote {len(events)} events to {out}")


@app.command()
def timeline(path: Path, out: Path = typer.Option(..., "--out", "-o")) -> None:
    """Generate a timeline markdown file from logs."""
    events = parse_file(path)
    content = build_timeline(events)
    _write_output(out, content)
    typer.echo(f"Wrote timeline to {out}")


@app.command()
def runbook(
    path: Path,
    out: Path = typer.Option(..., "--out", "-o"),
    title: str = typer.Option("Incident: Untitled", "--title"),
) -> None:
    """Generate a runbook skeleton from logs."""
    events = parse_file(path)
    content = build_runbook(events, title)
    _write_output(out, content)
    typer.echo(f"Wrote runbook to {out}")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
