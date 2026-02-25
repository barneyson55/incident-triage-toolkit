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
triage summary samples/app.log --out summary.json
triage timeline samples/app.log --out timeline.md
triage runbook samples/app.log --out runbook.md --title "Incident: Sample"
```

## Quickstart (PowerShell)
```powershell
py -3.11 -m venv .venv
. .venv\Scripts\Activate.ps1

python -m pip install -e ".[dev]"

triage parse samples/app.log --out parsed.json
triage summary samples/app.log --out summary.json
triage timeline samples/app.log --out timeline.md
triage runbook samples/app.log --out runbook.md --title "Incident: Sample"
```

## CLI Commands
- `triage parse <path> --out parsed.json`
- `triage summary <path> --out summary.json`
- `triage timeline <path> --out timeline.md`
- `triage runbook <path> --out runbook.md --title "Incident: ..."`

## Parse JSON output contract (current)
- Top-level payload keys are locked to: `schema_version`, `events`, `parse_summary`.
- Current parse payload version is `schema_version: "1.0.0"`.
- `events[*].timestamp` stays canonical UTC (`+00:00`) for deterministic ordering.
- `events[*].source_timestamp` preserves the original timestamp token from input.
- `events[*].source_offset` preserves the original explicit offset (`Z`, `+HH:MM`, `-HH:MM`) or
  `null` when input had no explicit offset.
- Event keys for schema `1.0.0` are locked to:
  `timestamp`, `source_timestamp`, `source_offset`, `level`, `component`, `message`, `correlation_id`.

Compatibility rules:
- **Additive change** (new optional top-level or event fields): allowed with a schema **minor** bump.
- **Breaking change** (rename/remove/type change/order contract break): requires a schema **major** bump
  and explicit release notes.

Example parse payload:
```json
{
  "schema_version": "1.0.0",
  "events": [
    {
      "timestamp": "2025-01-01T00:00:01+00:00",
      "source_timestamp": "2024-12-31T19:00:01-05:00",
      "source_offset": "-05:00",
      "level": "INFO",
      "component": "api",
      "message": "hello",
      "correlation_id": null
    }
  ],
  "parse_summary": {
    "total_lines": 1,
    "parsed_lines": 1,
    "dropped_lines": 0,
    "drop_ratio": 0.0,
    "dropped_reasons": {}
  }
}
```

Timeline and runbook outputs continue to render UTC timestamps only.

## Summary JSON output contract (current)
- `triage summary` emits deterministic JSON with `schema_version: "1.0.0"`.
- Top-level keys: `schema_version`, `incident_window`, `event_count`, `error_count`,
  `top_components`, `top_error_signatures`, `correlation_id_coverage`, `parse_summary`.
- `incident_window.start/end` are canonical UTC ISO-8601 timestamps.
- `top_components` and `top_error_signatures` are sorted by `count DESC`, then `name ASC`.

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
