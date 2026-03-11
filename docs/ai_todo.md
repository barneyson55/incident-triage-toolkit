# ai_todo.md (deterministic)

Rule: work ONLY on the **first unchecked top-level** item.

Priority refresh basis: `docs/status.md` + `docs/critical_todo.md` + live repo verification (2026-03-11 19:03 UTC):
- `git status --short --branch` ✅ clean `main...origin/main`
- `make test` ✅ (`111 passed`)
- `docs/status.md` ✅ confirms ITK-024 is complete and explicitly queues ITK-025 next
- `docs/critical_todo.md` ✅ exists and has no open critical items
- Current repo facts from this maintenance pass:
  - dedicated golden fixtures now exist for `parse`, `summary`, `timeline`, and `runbook`
  - `triage_toolkit/evidence.py` now carries shared ordering/evidence behavior for multiple outputs, but still lacks direct unit coverage
  - `triage_toolkit/cli.py` now centralizes parse-summary merging, diagnostics budgeting, strict gates, and output-slice filters, but those paths are still protected mostly through broader CLI tests
- Highest-leverage remaining gaps after the latest verification:
  - helper-layer regressions in shared evidence or CLI plumbing are still slower to localize than they should be
  - the live queue should stay 3-7 items, so the next hardening step after ITK-025 is now explicit instead of implicit

## Open priorities (highest engineering impact first)

- [x] ITK-024 (P1): Add dedicated golden/contract coverage for the summary JSON automation surface
  - Why (impact): `triage summary` is the primary machine-readable handoff surface and already ships `schema_version: "1.1.0"`, `evidence_by_source`, and filter-aware incident slicing. Unlike parse/timeline/runbook, it still lacks a dedicated golden/contract suite that makes drift obvious in review.
  - DoD:
    - Add `tests/test_summary_contract.py` plus golden fixtures for single-input, multi-input, stdin-label, and empty/filter-miss summary outputs.
    - Lock the current summary contract for `schema_version`, `incident_window`, `event_count`, `error_count`, `top_components`, `top_error_signatures`, `evidence_by_source`, `correlation_id_coverage`, and `parse_summary`.
    - Keep fixture updates deliberate: any intentional summary contract change must update tests and `README.md` together.
  - Verification:
    - `pytest -q tests/test_summary_contract.py`
    - `pytest -q tests/test_cli.py -k "summary"`
    - `make test`

- [ ] ITK-025 (P1): Add direct unit coverage for shared evidence and ranking helpers
  - Why (impact): `triage_toolkit/evidence.py` now drives summary, timeline, and runbook behavior. A small helper regression can therefore break several surfaces at once while only failing through higher-level tests, which makes root cause slower to pinpoint.
  - DoD:
    - Add `tests/test_evidence.py` covering `is_error`, `order_events`, signature normalization/ranking, source-evidence ranking, component ranking, and representative correlation-ID selection.
    - Include tied-timestamp cases that prove helper-level ordering stays aligned with the documented CLI determinism contract.
    - Cover redaction-aware signature rendering without duplicating full markdown/JSON golden payloads.
  - Verification:
    - `pytest -q tests/test_evidence.py`
    - `pytest -q tests/test_cli.py -k "summary or redact or deterministic"`
    - `make test`

- [ ] ITK-026 (P2): Add direct unit coverage for shared CLI ingestion, strict-gate, and filter helpers
  - Why (impact): `triage_toolkit/cli.py` now owns parse-summary aggregation, diagnostics-budget carry-forward, strict parse gating, and reusable event-slice filters for `summary`, `timeline`, and `runbook`. Those behaviors are critical, but today most regressions would surface only through larger command-level tests.
  - DoD:
    - Add `tests/test_cli_helpers.py` covering `_merge_parse_summaries`, `_apply_event_filters`, `_strict_parse_error`, and `_read_events_for_parse` behavior for per-source ordering and bounded diagnostics carry-forward.
    - Lock repeated-flag OR semantics, cross-filter AND semantics, aggregate drop-ratio rounding, and the rule that filters never mutate or bypass raw `parse_summary` quality signals.
    - Keep helper expectations aligned with the public CLI/README contract rather than inventing a separate private contract.
  - Verification:
    - `pytest -q tests/test_cli_helpers.py`
    - `pytest -q tests/test_cli.py -k "strict or filter or diagnostics or per_source"`
    - `make test`

---

Recently completed (kept brief so the live queue stays short):

- [x] ITK-023 (P1): Make equal-timestamp determinism explicit across shared ordering helpers
- [x] ITK-022 (P1): Finish per-source evidence concentration in timeline and runbook output
- [x] ITK-021 (P1): Add deterministic redaction controls for diagnostics and evidence surfaces
- [x] ITK-020 (P1): Preserve source provenance for successful parsed events and rendered evidence
- [x] ITK-019 (P1): Unify incident evidence semantics across `summary`, `timeline`, and `runbook`
- [x] ITK-017 (P1): Make runbook output evidence-driven instead of mostly boilerplate
- [x] ITK-016 (P1): Finish deterministic incident-slicing filter parity for `timeline` and `runbook`
- [x] ITK-018 (P1): Support stdin ingestion (`-`) across CLI commands

Completed foundation (kept brief for history):

- [x] ITK-001: Add installable packaging + `triage` console script
- [x] ITK-002: Add CI (GitHub Actions) for lint + tests
- [x] ITK-003: CLI UX improvements (stdout output, file errors, `--version`)
- [x] ITK-004 (P0): Add parse-quality gate to prevent silent data loss
- [x] ITK-005 (P0): Refactor ingestion to stream line-by-line (large-file safe)
- [x] ITK-006 (P0): Normalize outputs to UTC and accept offset-heavy text logs
- [x] ITK-007 (P1): Add machine-readable incident summary output for automation
- [x] ITK-008 (P0): Expand regression matrix and raise CI confidence margin before new feature work
- [x] ITK-009 (P1): Apply parse-quality gates to `timeline` and `runbook` commands
- [x] ITK-010 (P1): Preserve timezone provenance while keeping UTC as canonical output
- [x] ITK-011 (P1): Version and lock the parse JSON contract before further output expansion
- [x] ITK-012 (P2): Add multi-source ingestion (multiple files) with deterministic merge order
- [x] ITK-013 (P2): Add golden-output contract tests for parse/timeline/runbook determinism
- [x] ITK-014 (P1): Extend `triage summary` to multi-input parity
- [x] ITK-015 (P1): Add deterministic dropped-line diagnostics for parse quality investigation
