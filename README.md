# Incident Triage Toolkit

[![CI](https://github.com/barneyson55/incident-triage-toolkit/actions/workflows/ci.yml/badge.svg)](https://github.com/barneyson55/incident-triage-toolkit/actions/workflows/ci.yml)

A Python CLI to parse heterogeneous logs, generate an incident timeline, and
draft an RCA/runbook skeleton. It supports JSON lines and plain text log
formats and produces normalized outputs that are easy to share during support
triage.

## Why it matters for Application Support
- Quickly normalize mixed logs into a single timeline.
- Identify error patterns and suspected components faster.
- Produce a consistent runbook skeleton for handoffs and follow-ups.

## Quickstart (Linux/macOS / WSL)
```bash
python3 -m venv .venv
source .venv/bin/activate

python -m pip install -e ".[dev]"

triage parse samples/app.log --out parsed.json
triage timeline samples/app.log --out timeline.md
triage runbook samples/app.log --out runbook.md --title "Incident: Sample"
```

## Quickstart (PowerShell)
```powershell
py -3.11 -m venv .venv
. .venv\Scripts\Activate.ps1

python -m pip install -e ".[dev]"

triage parse samples/app.log --out parsed.json
triage timeline samples/app.log --out timeline.md
triage runbook samples/app.log --out runbook.md --title "Incident: Sample"
```

## CLI Commands
- `triage parse <path> --out parsed.json`
- `triage timeline <path> --out timeline.md`
- `triage runbook <path> --out runbook.md --title "Incident: ..."`

## Makefile (Linux/macOS / WSL)
```bash
make setup
make lint
make test
make run
```

## Notes
- You can always run the CLI without the console script:
  - `python -m triage_toolkit.cli ...`
  - `python -m triage_toolkit ...`
