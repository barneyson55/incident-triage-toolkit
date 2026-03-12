# ai_todo.md (deterministic)

Rule: work ONLY on the **first unchecked top-level** item.

Priority refresh basis: `docs/status.md` + `docs/critical_todo.md` + live repo/doc verification (2026-03-12 13:49 UTC):
- `git status --short --branch` ⚠️ `main...origin/main` with pre-existing docs-only changes already present in `docs/status.md` and `docs/user_todo.md`
- `docs/status.md` ✅ exists and records ITK-027 as complete while explicitly queuing ITK-028 next
- `docs/critical_todo.md` ✅ exists and still has no open critical items
- `docs/ai_todo.md` ✅ exists and needed refresh because the repo-fact snapshot was one maintenance pass behind and still treated parser-helper hardening as clearly ahead of all remaining public-surface gaps
- `docs/deep_research_auto.md` ✅ exists and was refreshed to reflect the current architecture/coverage map
- Current repo facts from this maintenance pass:
  - the package is still intentionally small and layered: `parser.py` + `utils.py` ingest, `cli.py` orchestrates commands/strict gates, `evidence.py` + `redaction.py` provide shared semantics, and `timeline.py` / `runbook.py` render operator-facing markdown
  - current repo footprint is compact but mature for its size: 10 source modules, 10 test modules, 130 test functions, and 11 golden fixtures
  - dedicated helper suites already exist for shared CLI plumbing, evidence logic, and redaction behavior (`tests/test_cli_helpers.py`, `tests/test_evidence.py`, `tests/test_redaction.py`)
  - dedicated contract/golden coverage already exists for the current non-redacted `parse`, `summary`, `timeline`, and `runbook` surfaces
  - there is still no dedicated cross-surface parity suite proving `summary`, `timeline`, and `runbook` stay aligned on the same filtered incident slice (`tests/test_output_parity.py` is still missing)
  - there are still no redacted golden fixtures freezing the full rendered outputs for parse diagnostics, timeline markdown, and runbook markdown
  - parser coverage is already broad at the public-behavior level (`tests/test_parser.py`), but helper-builder invariants like explicit provenance extraction, dropped-line diagnostic builders, and `source_order` propagation are still protected mostly through broader command tests
  - `tests/test_utils.py` remains intentionally light and currently covers timestamp normalization only; direct `extract_correlation_id(...)` behavior is still mostly exercised indirectly through parser/evidence tests
  - latest recorded verification in `docs/status.md` is `make test` ✅ (`130 passed`)

## Open priorities (highest engineering impact first)

- [x] ITK-028 (P1): Add a fixture-driven parity suite proving `summary`, `timeline`, and `runbook` stay aligned on the same filtered incident slice
  - Why (impact): the repo now depends on shared evidence/filtering/order semantics across three operator-facing surfaces. Individual command tests can all pass while incident windows, signature ranking, source concentration, or empty-slice behavior drift across JSON vs markdown outputs. A parity suite is the highest-leverage missing regression net.
  - DoD:
    - Add a dedicated parity test module (for example `tests/test_output_parity.py`) that drives the same multi-input fixture through `summary`, `timeline`, and `runbook`.
    - Assert the same filtered slice yields matching first/last observed timestamps, evidence-event counts, top signature ordering, and source concentration ordering across all three surfaces.
    - Include at least one file+stdin case and one empty-slice case so parity holds for the two highest-risk shared paths.
  - Verification:
    - `pytest -q tests/test_output_parity.py`
    - `pytest -q tests/test_cli.py -k "summary or timeline or runbook"`
    - `make test`

- [ ] ITK-030 (P2): Add full redacted golden fixtures for parse diagnostics, timeline, and runbook outputs
  - Why (impact): redaction is now a user-facing sharing/safety feature, but the repo still freezes it only through targeted substring assertions. Full golden fixtures would catch section-order drift, placeholder-placement drift, and markdown/JSON formatting regressions that helper tests will not see.
  - DoD:
    - Add compact golden fixtures for `triage parse --redact --diagnostics-limit N`, `triage timeline --redact`, and `triage runbook --redact`.
    - Assert stable placeholder reuse across the full outputs rather than only checking a few substrings.
    - Reuse one compact sensitive fixture so the goldens stay reviewable and cheap to maintain.
  - Verification:
    - `pytest -q tests/test_cli.py -k "redact"`
    - `pytest -q tests/test_timeline.py -k "redact"`
    - `pytest -q tests/test_runbook.py -k "redact"`
    - `make test`

- [ ] ITK-029 (P2): Tighten parser helper coverage for provenance extraction, diagnostics builders, and source-order propagation
  - Why (impact): `triage_toolkit/parser.py` is still the ingestion root for every command. Public parser behavior is already decently covered, but several small helper/builder paths still fail only indirectly even though they control provenance metadata, drop diagnostics, and source-order propagation used later by the shared ordering helpers.
  - DoD:
    - Expand parser-focused tests to cover `_source_timestamp_provenance`, `_build_parse_summary`, `_build_dropped_line_diagnostic`, and `source_order` propagation through `parse_lines_with_summary`.
    - Lock mixed JSON/text drop-reason boundaries so invalid JSON, non-object JSON, missing timestamps, invalid timestamps, blank lines, and unrecognized text stay classified as documented.
    - Keep expectations on public event/summary fields and deterministic ordering, not on incidental internal iteration details.
  - Verification:
    - `pytest -q tests/test_parser.py -k "provenance or diagnostics or source_order or dropped_reason"`
    - `pytest -q tests/test_cli.py -k "parse and provenance"`
    - `make test`

- [ ] ITK-031 (P3): Add direct utility-edge coverage for timestamp normalization and correlation-ID extraction helpers
  - Why (impact): `utils.py` is tiny but sits under every parse path. Its current direct test surface is narrow relative to how much parser behavior depends on it, especially for correlation-ID extraction and timestamp-shape edge cases.
  - DoD:
    - Expand `tests/test_utils.py` to cover `extract_correlation_id(...)` for supported `cid=` / `correlation_id=` message patterns plus clear non-match cases.
    - Add timestamp helper cases for microseconds, naive vs offset-aware inputs, `T` vs space separators, and invalid offset/timestamp shapes.
    - Keep the suite focused on documented helper behavior rather than duplicating end-to-end parser tests wholesale.
  - Verification:
    - `pytest -q tests/test_utils.py`
    - `pytest -q tests/test_parser.py -k "timestamp or correlation"`
    - `make test`

---

Recently completed (kept brief so the live queue stays short):

- [x] ITK-027 (P1): Add direct unit coverage for shared redaction helpers and placeholder stability
- [x] ITK-026 (P1): Add direct unit coverage for shared CLI ingestion, strict-gate, filter, and write-path helpers
- [x] ITK-025 (P1): Add direct unit coverage for shared evidence and ranking helpers
- [x] ITK-024 (P1): Add dedicated golden/contract coverage for the summary JSON automation surface
- [x] ITK-023 (P1): Make equal-timestamp determinism explicit across shared ordering helpers
- [x] ITK-022 (P1): Finish per-source evidence concentration in timeline and runbook output
- [x] ITK-021 (P1): Add deterministic redaction controls for diagnostics and evidence surfaces
- [x] ITK-020 (P1): Preserve source provenance for successful parsed events and rendered evidence
- [x] ITK-019 (P1): Unify incident evidence semantics across `summary`, `timeline`, and `runbook`
- [x] ITK-018 (P1): Support stdin ingestion (`-`) across CLI commands
- [x] ITK-017 (P1): Make runbook output evidence-driven instead of mostly boilerplate
- [x] ITK-016 (P1): Finish deterministic incident-slicing filter parity for `timeline` and `runbook`

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
