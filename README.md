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
- `triage parse <path...> --out parsed.json --diagnostics-limit 5 --redact`
- `triage summary <path...> --out summary.json`
- `triage timeline <path...> --out timeline.md`
- `triage timeline <path...> --out timeline.md --redact`
- `triage runbook <path...> --out runbook.md --title "Incident: ..."`
- `triage runbook <path...> --out runbook.md --title "Incident: ..." --redact`

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

## Stdin ingestion (`-`)
`triage parse`, `summary`, `timeline`, and `runbook` all accept `-` as a UTF-8 stdin source.

Examples:
```bash
kubectl logs deploy/api --since=15m | triage parse - --out parsed.json
journalctl -u myservice --since "1 hour ago" | triage summary - --out summary.json
cat samples/app.log | triage timeline - --out timeline.md
cat samples/app.log | triage runbook - --out runbook.md --title "Incident: STDIN"
triage parse app.log - --out parsed.json   # file first, stdin second
```

Stdin mixing rules:
- `-` may appear at most once in a command.
- `-` is reported back as the stable source label in `parse_summary.per_source[*].path`
  and dropped-line diagnostics (`source_path`).
- When files and stdin are combined, merge ordering stays deterministic: UTC timestamp,
  then CLI input position (including `-`), then original line order within that source.
- In PowerShell, prefer `Get-Content -Raw .\app.log | triage parse - --out parsed.json`
  so the native CLI receives newline-delimited text predictably.

For parse-quality investigation, `triage parse --diagnostics-limit N` adds a bounded
`parse_summary.dropped_line_diagnostics` list. Entries are emitted in deterministic
CLI input order, then by original line number within each source file. Each entry
includes `source_path`, `line_number`, `reason`, and the raw rejected `raw_line`.
Adding `--redact` preserves the same ordering/counters but rewrites `raw_line` with
stable placeholders for emails, IPs, UUID/correlation-style identifiers, and long
token-like secrets. Redaction happens after parse-quality evaluation, so strict-gate
behavior and dropped-line classification do not change.

## Parse JSON output contract (current)
- Top-level payload keys are locked to: `schema_version`, `events`, `parse_summary`.
- Current parse payload version is `schema_version: "1.2.0"`.
- `events[*].timestamp` stays canonical UTC (`+00:00`) for deterministic ordering.
- `events[*].source_timestamp` preserves the original timestamp token from input.
- `events[*].source_offset` preserves the original explicit offset (`Z`, `+HH:MM`, `-HH:MM`) or
  `null` when input had no explicit offset.
- `events[*].source_path` preserves the original source label for successful events (file path or stable stdin label `-`).
- `events[*].line_number` preserves the original 1-based line number within that source.
- Event keys for schema `1.2.0` are locked to:
  `timestamp`, `source_timestamp`, `source_offset`, `source_path`, `line_number`, `level`, `component`, `message`, `correlation_id`.
- `parse_summary.dropped_line_diagnostics` is optional and only present when `--diagnostics-limit > 0`.
  It contains the first `N` dropped lines in deterministic input order and line order.

Compatibility rules:
- **Additive change** (new optional top-level or event fields): allowed with a schema **minor** bump.
- **Breaking change** (rename/remove/type change/order contract break): requires a schema **major** bump
  and explicit release notes.

Example parse payload:
```json
{
  "schema_version": "1.2.0",
  "events": [
    {
      "timestamp": "2025-01-01T00:00:01+00:00",
      "source_timestamp": "2024-12-31T19:00:01-05:00",
      "source_offset": "-05:00",
      "source_path": "samples/app.log",
      "line_number": 1,
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

Timeline and runbook outputs continue to render UTC timestamps only, but now cite source provenance as `source_path:line_number` in event/evidence surfaces.
When you add `--redact`, those human-readable surfaces keep the same event/evidence ordering but replace sensitive values with stable placeholders such as `[redacted-email:...]`, `[redacted-ip:...]`, `[redacted-id:...]`, and `[redacted-secret:...]`.

### Opt-in redaction mode (`--redact`)
- `triage parse --redact` redacts only `parse_summary.dropped_line_diagnostics[*].raw_line`.
- `triage timeline --redact` redacts rendered message cells plus the "Notable Errors" evidence section.
- `triage runbook --redact` redacts rendered evidence/example sections and representative correlation IDs.
- Placeholders are deterministic for the matched value, so the same email/IP/ID/secret is rendered with the same placeholder across parse diagnostics, timeline output, and runbook output.
- Built-in redaction is intentionally narrow and best-effort: it does **not** rewrite source paths, the structured `events[*]` payload in `triage parse`, or the machine-readable `triage summary` JSON contract.
- Because redaction is render-time only, parse counters, strict gates, evidence selection, and overall ordering remain unchanged.

## Summary JSON output contract (current)
- `triage summary` emits deterministic JSON with `schema_version: "1.1.0"`.
- Top-level keys: `schema_version`, `incident_window`, `event_count`, `error_count`,
  `top_components`, `top_error_signatures`, `evidence_by_source`, `correlation_id_coverage`, `parse_summary`.
- `incident_window.start/end` are canonical UTC ISO-8601 timestamps across the merged event set.
- `top_components` is sorted by `count DESC`, then `name ASC`.
- `top_error_signatures` uses the same shared incident-evidence rules as timeline/runbook:
  - evidence events include levels `ERROR`, `CRITICAL`, and `FATAL`
  - events whose message text contains `error` also count as evidence, even if the level is lower
  - signatures are normalized to lowercase, correlation IDs become `cid=<id>`, and digit runs become `#`
  - signature ordering is deterministic: `count DESC`, then earliest evidence timestamp, then normalized signature text
- `evidence_by_source` counts those same evidence events per stable source label (file path or `-` for stdin).
  Ordering is deterministic: `count DESC`, then earliest evidence timestamp for that source, then source label text.
- Multi-input runs use the same deterministic merge contract as `parse`/`timeline`/`runbook`
  (UTC timestamp, then CLI input order, then line order within source).
- `parse_summary` stays backward compatible for single-input runs; multi-input runs add ordered
  `per_source` entries (in the exact CLI input order) alongside aggregate counters.

### Deterministic incident slicing filters
`triage summary`, `triage timeline`, and `triage runbook` all support the same repeated output-slicing flags:

```bash
triage summary samples/app.log --out summary.json --component api --level error
triage timeline samples/app.log --out timeline.md --component api --component worker --correlation-id c-123
triage runbook samples/app.log --out runbook.md --title "Incident: Slice" --component worker --level error
```

Filter semantics:
- Repeating the same flag widens the match with OR semantics.
- Different filter families combine with AND semantics.
- `--level` is case-insensitive and matches normalized event levels.
- `--component` and `--correlation-id` use exact string matching on parsed event fields.
- Filtered `summary`, `timeline`, and `runbook` outputs preserve the existing deterministic event ordering.
- Strict parse gates and `parse_summary` always reflect the raw ingested inputs before filtering,
  so filters cannot hide parse failures or dropped-line ratios.
- If filters match no events, `summary` counters become zero/empty while `timeline` and `runbook`
  render their empty-state templates; in all cases the raw ingestion quality remains unchanged.

### Runbook output structure
`triage runbook` now includes deterministic evidence sections derived from the parsed event slice:
- incident window, first/last observed timestamps, and evidence-event counts
- top normalized error signatures with counts and first/last seen timestamps
- suspected components with error counts
- representative correlation IDs from the evidence slice
- 1-3 representative failures, chosen deterministically as the earliest occurrence for each top signature

The runbook remains UTC-first. If filters remove all matching events (or no error-like evidence exists in the slice), the markdown switches to an explicit no-evidence template instead of generic filler.

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
