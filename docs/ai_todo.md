# ai_todo.md (deterministic)

Rule: work ONLY on the **first unchecked top-level** item.

Priority refresh basis: `docs/status.md` + `docs/critical_todo.md` + live repo verification (2026-03-11 16:58 UTC):
- `git status --short --branch` ✅ clean `main...origin/main`
- `make test` ✅ (98 passed)
- `docs/status.md` ✅ confirms ITK-021 is complete and ITK-022 is partially shipped (`summary` JSON now exposes `evidence_by_source`)
- `docs/critical_todo.md` ✅ exists and has no open critical items
- Highest-leverage remaining gaps after the latest verification:
  - per-source evidence concentration is now visible in `triage summary`, but timeline/runbook still do not summarize which source dominates the incident slice
  - equal-timestamp determinism in shared helpers is still partly implicit and currently leans on Python stable-sort behavior plus caller-preserved order
  - the summary JSON automation surface is richer (`schema_version: 1.1.0`) but still lacks dedicated golden/contract locking before further output expansion

## Open priorities (highest engineering impact first)

- [x] ITK-022 (P1): Finish per-source evidence concentration in timeline and runbook output
  - Why (impact): successful-event provenance is already shipped and `triage summary` already exposes `evidence_by_source`, but the two human-readable handoff surfaces still make operators infer source dominance manually.
  - DoD:
    - Add concise per-source evidence callouts to timeline and runbook using the same source labels and evidence semantics already used by `summary`.
    - Keep deterministic source ordering aligned with the current summary contract: `count DESC`, then earliest evidence timestamp, then source label text.
    - Preserve existing filters, redaction behavior, UTC rendering, and event/example ordering.
    - Update README and regression coverage for the new source-focused output sections.
  - Verification:
    - `pytest -q tests/test_timeline.py -k "source"`
    - `pytest -q tests/test_runbook.py -k "source"`
    - `pytest -q tests/test_cli.py -k "summary and source"`
    - `make test`

- [ ] ITK-023 (P1): Make equal-timestamp determinism explicit across shared ordering helpers
  - Why (impact): `triage_toolkit/evidence.py` still re-sorts events by timestamp only, so downstream determinism depends on Python stable sort and callers already preserving CLI merge order. That works today, but it is an implicit implementation detail rather than an explicit product contract.
  - DoD:
    - Centralize one explicit same-timestamp ordering contract for parse/timeline/runbook/evidence helper paths.
    - Preserve the documented merge semantics end-to-end: canonical UTC timestamp, then CLI input order (including `-`), then original line order within the source.
    - Add regression cases for multi-file and file+stdin same-timestamp incidents, including filtered slices.
    - Document the explicit tie-break contract in README.
  - Verification:
    - `pytest -q tests/test_cli.py -k "stdin or tied or order"`
    - `pytest -q tests/test_timeline.py -k "order or deterministic"`
    - `pytest -q tests/test_runbook.py -k "order or deterministic"`
    - `make test`

- [ ] ITK-024 (P2): Add dedicated golden/contract coverage for the summary JSON automation surface
  - Why (impact): `triage summary` is now the main machine-readable handoff surface for automation and already carries `evidence_by_source`, but unlike parse/timeline/runbook it still lacks dedicated golden fixtures that make contract drift obvious in review.
  - DoD:
    - Add dedicated summary contract/golden tests for single-input, multi-input, stdin-label, and empty/filter-miss cases.
    - Lock the current `schema_version`, output shape, and deterministic ordering for `incident_window`, `top_components`, `top_error_signatures`, `evidence_by_source`, `correlation_id_coverage`, and `parse_summary`.
    - Update README examples only if the locked summary contract changes deliberately.
  - Verification:
    - `pytest -q tests/test_cli.py -k "summary and (schema or contract or golden)"`
    - `make test`

---

Recently completed (kept brief so the live queue stays short):

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
