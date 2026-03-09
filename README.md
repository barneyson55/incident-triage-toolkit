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
triage parse samples/app.log --out parsed.json --diagnostics-limit 5
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
triage parse samples/app.log --out parsed.json --diagnostics-limit 5
triage summary samples/app.log --out summary.json
triage timeline samples/app.log --out timeline.md
triage runbook samples/app.log --out runbook.md --title "Incident: Sample"
```

## CLI Commands
- `triage parse <path...> --out parsed.json`
- `triage parse <path...> --out parsed.json --diagnostics-limit 5`
- `triage summary <path...> --out summary.json`
- `triage timeline <path...> --out timeline.md`
- `triage runbook <path...> --out runbook.md --title "Incident: ..."`

## Multi-input ingestion & deterministic merge semantics
`parse`, `summary`, `timeline`, and `runbook` accept multiple input files in one command.

Example:
```bash
triage parse logs/api.log logs/web.log logs/db.log --out parsed.json
triage summary logs/api.log logs/web.log logs/db.log --out summary.json
triage timeline logs/api.log logs/web.log --out timeline.md
triage runbook logs/api.log logs/web.log --out runbook.md --title "Incident: 2025-01-01"
```

Deterministic ordering contract:
1. Canonical UTC timestamp ascending (`events[*].timestamp`).
2. If timestamps tie, earlier CLI input path wins.
3. If still tied, original line order inside that source file wins.

For multi-input `triage parse`, `parse_summary` includes aggregate counters plus
`per_source` (ordered exactly as CLI inputs), each with the same summary fields
(`total_lines`, `parsed_lines`, `dropped_lines`, `drop_ratio`, `dropped_reasons`).

For parse-quality investigation, `triage parse --diagnostics-limit N` adds a bounded
`parse_summary.dropped_line_diagnostics` list. Entries are emitted in deterministic
CLI input order, then by original line number within each source file. Each entry
includes `source_path`, `line_number`, `reason`, and the raw rejected `raw_line`.
Diagnostics are copied verbatim from input lines, so redact sensitive logs upstream
if needed before sharing the JSON output.

## Parse JSON output contract (current)
- Top-level payload keys are locked to: `schema_version`, `events`, `parse_summary`.
- Current parse payload version is `schema_version: "1.1.0"`.
- `events[*].timestamp` stays canonical UTC (`+00:00`) for deterministic ordering.
- `events[*].source_timestamp` preserves the original timestamp token from input.
- `events[*].source_offset` preserves the original explicit offset (`Z`, `+HH:MM`, `-HH:MM`) or
  `null` when input had no explicit offset.
- Event keys for schema `1.1.0` are locked to:
  `timestamp`, `source_timestamp`, `source_offset`, `level`, `component`, `message`, `correlation_id`.
- `parse_summary.dropped_line_diagnostics` is optional and only present when `--diagnostics-limit > 0`.
  It contains the first `N` dropped lines in deterministic input order and line order.

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
- `incident_window.start/end` are canonical UTC ISO-8601 timestamps across the merged event set.
- `top_components` and `top_error_signatures` are sorted by `count DESC`, then `name ASC`.
- Multi-input runs use the same deterministic merge contract as `parse`/`timeline`/`runbook`
  (UTC timestamp, then CLI input order, then line order within source).
- `parse_summary` stays backward compatible for single-input runs; multi-input runs add ordered
  `per_source` entries (in the exact CLI input order) alongside aggregate counters.

### Deterministic incident slicing filters (current milestone)
`triage summary` now supports repeated output-slicing flags:

```bash
triage summary samples/app.log --out summary.json --component api --level error
triage summary samples/app.log --out summary.json --component api --component worker --correlation-id c-123
```

Filter semantics:
- Repeating the same flag widens the match with OR semantics.
- Different filter families combine with AND semantics.
- `--level` is case-insensitive and matches normalized event levels.
- `--component` and `--correlation-id` use exact string matching on parsed event fields.
- Strict parse gates and `parse_summary` always reflect the raw ingested inputs before filtering,
  so filters cannot hide parse failures or dropped-line ratios.
- If filters match no events, summary counters become zero/empty while `parse_summary` still
  reports the raw ingestion quality.

`timeline` and `runbook` filter flags are still pending as follow-up work under ITK-016.

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
