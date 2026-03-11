# ai_todo.md (deterministic)

Rule: work ONLY on the **first unchecked top-level** item.

Priority refresh basis: `docs/status.md` + `docs/critical_todo.md` + live repo verification (2026-03-11 18:02 UTC):
- `git status --short --branch` ✅ clean `main...origin/main`
- `make test` ✅ (`102 passed`)
- `docs/status.md` ✅ confirms ITK-022 is complete and explicitly queues ITK-023 next
- `docs/critical_todo.md` ✅ exists and has no open critical items
- Highest-leverage remaining gaps after the latest verification:
  - `triage summary` is now a versioned automation surface, but it still lacks dedicated golden/contract fixtures of its own
  - shared evidence/ranking semantics are still protected mostly indirectly via CLI/timeline/runbook tests, which makes regressions slower to localize

## Open priorities (highest engineering impact first)

- [ ] ITK-024 (P2): Add dedicated golden/contract coverage for the summary JSON automation surface
  - Why (impact): `triage summary` is now the main machine-readable handoff surface and already carries `schema_version: "1.1.0"` plus `evidence_by_source`, but unlike parse/timeline/runbook it still lacks dedicated fixtures that make contract drift obvious in review.
  - DoD:
    - Add `tests/test_summary_contract.py` plus focused golden fixtures for single-input, multi-input, stdin-label, and empty/filter-miss summary outputs.
    - Lock the current summary contract for `schema_version`, `incident_window`, `event_count`, `error_count`, `top_components`, `top_error_signatures`, `evidence_by_source`, `correlation_id_coverage`, and `parse_summary`.
    - Keep fixture updates deliberate: any intentional contract change must update tests and README together.
  - Verification:
    - `pytest -q tests/test_summary_contract.py`
    - `pytest -q tests/test_cli.py -k "summary"`
    - `make test`

- [ ] ITK-025 (P2): Add direct unit coverage for shared evidence and ranking helpers
  - Why (impact): `triage_toolkit/evidence.py` now drives summary, timeline, and runbook behavior, but most protection is still indirect through higher-level outputs. A small helper regression can therefore break several surfaces at once while making root cause slower to pinpoint.
  - DoD:
    - Add `tests/test_evidence.py` covering `is_error`, `order_events`, signature normalization/ranking, source-evidence ranking, and representative correlation-ID selection.
    - Include tied-timestamp cases that prove helper-level ordering stays aligned with the CLI determinism contract.
    - Cover redaction-aware signature rendering without duplicating full markdown/JSON golden payloads.
  - Verification:
    - `pytest -q tests/test_evidence.py`
    - `pytest -q tests/test_cli.py -k "summary or redact"`
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
