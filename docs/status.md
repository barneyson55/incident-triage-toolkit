# status.md

## Current state
- Repo: incident-triage-toolkit (Python CLI)
- Goal: parse heterogeneous logs, generate a timeline, and draft an RCA/runbook skeleton.

## Work mode
- Deterministic TODO: `docs/ai_todo.md` (first unchecked top-level only)
- If `docs/user_todo.md` has any unchecked items → STOP.

## Latest updates
- ITK-023 completed (equal-timestamp determinism is now explicit across parse + helper paths):
  - `triage_toolkit/models.py` now carries an internal `source_order` field on `LogEvent`, so multi-input CLI ingestion can preserve explicit source-position metadata without changing the public JSON contract.
  - `triage_toolkit/parser.py`, `triage_toolkit/cli.py`, and `triage_toolkit/evidence.py` now propagate that source-order metadata from multi-file/stdin ingestion and use one shared `order_events(...)` tie-break path: UTC timestamp, then source order (or stable source label fallback), then original line number, then original iterable position.
  - `tests/test_timeline.py` and `tests/test_runbook.py` now lock same-timestamp filtered-slice behavior for both multi-file and file+stdin inputs, even when helper callers pass the events in reverse order.
  - `tests/test_cli.py` was updated for the internal parser call-shape change, and `README.md` now says explicitly that filtered `summary`/`timeline`/`runbook` slices keep the CLI tie-break contract instead of depending on stable sort behavior.
- Why:
  - Deterministic same-timestamp ordering is now an explicit shared implementation detail rather than an accidental property of already-sorted caller input, which lowers regression risk across parse, summary, timeline, and runbook surfaces.
- Risks / follow-ups:
  - The public parse/summary contracts are unchanged, but helper-level fallback ordering for events that do not carry CLI source metadata still uses stable source labels or original iterable position; dedicated helper unit coverage is still queued in ITK-025.
  - Dedicated golden/contract tests for the summary JSON automation surface are still queued in ITK-024.
- Verification run:
  - `.venv/bin/python -m pytest -q tests/test_cli.py -k "same_timestamp or tied or stdin"` ✅ (10 passed)
  - `.venv/bin/python -m pytest -q tests/test_timeline.py -k "ordering or deterministic"` ✅ (5 passed)
  - `.venv/bin/python -m pytest -q tests/test_runbook.py -k "deterministic or filtered"` ✅ (6 passed)
  - `make lint` ✅
  - `make test` ✅ (106 passed)
- ITK-022 completed (per-source evidence concentration now reaches all operator-facing outputs):
  - `triage_toolkit/timeline.py` now renders an `Evidence by Source` section using the shared evidence semantics and deterministic source ordering (`count DESC`, earliest evidence timestamp, source label text).
  - `triage_toolkit/runbook.py` now adds concise source-concentration callouts in both the Symptoms summary and the Evidence section, without changing UTC rendering, filters, redaction behavior, or representative-example ordering.
  - `tests/test_timeline.py`, `tests/test_runbook.py`, and `tests/test_cli.py` now lock the new source-ranked output sections and ordering behavior.
  - `tests/fixtures/golden/timeline_output.md` and `tests/fixtures/golden/runbook_output.md` now include the new source-focused sections.
  - `README.md` now documents the timeline/runbook source-concentration surfaces alongside the existing summary contract.
- Why:
  - Operators can now see which source dominates the incident evidence slice directly in timeline and runbook handoff artifacts, not just in the machine-readable summary JSON.
- Risks / follow-ups:
  - Equal-timestamp behavior is still partly implicit in shared ordering helpers and is queued next in ITK-023.
- Verification run:
  - `.venv/bin/python -m pytest -q tests/test_timeline.py -k "source"` ✅ (2 passed)
  - `.venv/bin/python -m pytest -q tests/test_runbook.py -k "source"` ✅ (2 passed)
  - `.venv/bin/python -m pytest -q tests/test_cli.py -k "summary and source"` ✅ (4 passed)
  - `make lint` ✅
  - `make test` ✅ (102 passed)
- ITK-021 completed (deterministic redaction controls for diagnostics and evidence surfaces):
  - Added `triage_toolkit/redaction.py`, a shared render-time redaction helper that emits stable placeholders for emails, IPs, UUID/correlation-style identifiers, and long token-like secrets.
  - `triage_toolkit/cli.py` now supports opt-in `--redact` on `parse`, `timeline`, and `runbook`; parse redaction only rewrites `parse_summary.dropped_line_diagnostics[*].raw_line`, so raw event payloads, counters, and strict gates stay unchanged.
  - `triage_toolkit/evidence.py`, `triage_toolkit/timeline.py`, and `triage_toolkit/runbook.py` now preserve the existing evidence ordering/grouping while redacting rendered message/evidence/example surfaces and representative correlation IDs at output time.
  - `tests/test_cli.py`, `tests/test_timeline.py`, and `tests/test_runbook.py` now lock the cross-surface redaction contract, including deterministic placeholder reuse across parse diagnostics, timeline output, and runbook output.
  - `README.md` now documents the `--redact` scope, placeholder policy, ordering guarantees, and the deliberate limits of built-in redaction.
- Why:
  - Operators can now share parse diagnostics and human-readable triage artifacts more safely without weakening parse-quality analysis or deterministic incident rendering.
- Risks / follow-ups:
  - Built-in redaction is intentionally narrow/best-effort and does not rewrite structured `triage parse` event payloads or the machine-readable `triage summary` JSON contract.
  - Follow-on work moved into ITK-022, which is now in progress with summary JSON complete and timeline/runbook source callouts still pending.
- Verification run:
  - `.venv/bin/python -m pytest -q tests/test_cli.py -k "redact or diagnostics"` ✅
  - `.venv/bin/python -m pytest -q tests/test_timeline.py -k "redact or evidence"` ✅
  - `.venv/bin/python -m pytest -q tests/test_runbook.py -k "redact or evidence"` ✅
  - `make lint` ✅
  - `make test` ✅ (97 passed)

## Next
- Start ITK-024 by adding dedicated golden/contract coverage for the summary JSON automation surface.
