# status.md

## Current state
- Repo: incident-triage-toolkit (Python CLI)
- Goal: parse heterogeneous logs, generate a timeline, and draft an RCA/runbook skeleton.

## Work mode
- Deterministic TODO: `docs/ai_todo.md` (first unchecked top-level only)
- If `docs/user_todo.md` has any unchecked items → STOP.

## Latest updates
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
- Start ITK-023 by making equal-timestamp determinism explicit across shared ordering helpers.
