# Incident Triage Toolkit

A Python CLI to parse heterogeneous logs, generate an incident timeline, and
draft an RCA/runbook skeleton. It supports JSON lines and plain text log
formats and produces normalized outputs that are easy to share during support
triage.

## Why it matters for Application Support
- Quickly normalize mixed logs into a single timeline.
- Identify error patterns and suspected components faster.
- Produce a consistent runbook skeleton for handoffs and follow-ups.

## Quickstart (PowerShell)
```powershell
py -3.11 -m venv .venv
. .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt -r requirements-dev.txt

python -m triage_toolkit.cli parse samples/app.log --out parsed.json
python -m triage_toolkit.cli timeline samples/app.log --out timeline.md
python -m triage_toolkit.cli runbook samples/app.log --out runbook.md --title "Incident: Sample"
```

## CLI Commands
- `triage parse <path> --out parsed.json`
- `triage timeline <path> --out timeline.md`
- `triage runbook <path> --out runbook.md --title "Incident: ..."`

## Makefile
```bash
make setup
make lint
make test
make run
```

## Notes
- Use `python -m triage_toolkit` as a portable entrypoint if you do not have a
  `triage` console script installed.
