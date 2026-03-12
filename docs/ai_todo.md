# ai_todo.md (deterministic)

Rule: work ONLY on the **first unchecked top-level** item.

Priority refresh basis: `docs/status.md` + `docs/critical_todo.md` + live repo/doc verification (2026-03-12 16:30 UTC):
- `git status --short --branch` ✅ working tree clean in this maintenance pass
- `docs/status.md` ✅ exists and records ITK-030 as complete while explicitly queuing ITK-029 next
- `docs/critical_todo.md` ✅ exists and still has no open critical items
- `docs/ai_todo.md` ✅ exists and needed refresh because the open queue had only two items and did not call out the remaining direct summary/redaction-helper gap
- `docs/deep_research_auto.md` ✅ exists and was refreshed in the same pass so the background note matches the live queue again
- Current repo facts from this maintenance pass:
  - the package remains intentionally compact and layered: `parser.py` + `utils.py` ingest, `cli.py` orchestrates commands/strict gates, `evidence.py` + `redaction.py` provide shared semantics, and `timeline.py` / `runbook.py` render operator-facing markdown
  - current repo footprint is stable and small enough for focused hardening: 10 source modules, 11 test modules, 135 test functions, and 15 golden fixtures
  - dedicated helper suites already exist for shared CLI plumbing, evidence logic, and redaction behavior (`tests/test_cli_helpers.py`, `tests/test_evidence.py`, `tests/test_redaction.py`)
  - dedicated contract/golden coverage already exists for the current parse, summary, timeline, and runbook surfaces, including full redacted goldens for parse diagnostics, timeline markdown, and runbook markdown
  - dedicated cross-surface parity coverage already exists in `tests/test_output_parity.py` and now locks the highest-risk shared filtered-slice seam
  - parser helper/builder invariants like explicit provenance extraction, dropped-line diagnostic builders, and `source_order` propagation are still protected mostly through broader parser/CLI tests instead of direct helper-focused coverage
  - `tests/test_utils.py` remains intentionally light and still covers less of the timestamp/correlation helper edge space than the parser stack depends on indirectly
  - `cli.py` still lacks direct helper-focused tests for `_top_items(...)`, `_build_incident_summary(...)`, and `_redact_parse_summary(...)`, even though those helpers shape the automation-facing summary contract and redacted parse diagnostics behavior
  - latest recorded verification in `docs/status.md` is `make test` ✅ (`135 passed`)

## Open priorities (highest engineering impact first)

- [x] ITK-029 (P2): Tighten parser helper coverage for provenance extraction, diagnostics builders, and source-order propagation
  - Why (impact): `triage_toolkit/parser.py` is still the ingestion root for every command. Public parser behavior is already well covered, but several small helper/builder paths still fail only indirectly even though they control provenance metadata, drop diagnostics, and source-order propagation used later by the shared ordering helpers.
  - DoD:
    - Expand parser-focused tests to cover `_source_timestamp_provenance`, `_build_parse_summary`, `_build_dropped_line_diagnostic`, and `source_order` propagation through `parse_lines_with_summary`.
    - Lock mixed JSON/text drop-reason boundaries so invalid JSON, non-object JSON, missing timestamps, invalid timestamps, blank lines, and unrecognized text stay classified as documented.
    - Keep expectations on public event/summary fields and deterministic ordering, not on incidental internal iteration details.
  - Verification:
    - `.venv/bin/python -m pytest -q tests/test_parser.py`
    - `.venv/bin/python -m pytest -q tests/test_cli.py -k "parse and provenance"`
    - `make test`

- [ ] ITK-032 (P2): Add direct CLI summary/redaction helper coverage for automation-facing ordering invariants
  - Why (impact): `triage summary` is the machine-readable handoff surface, and parse redaction is the main share-safe diagnostics path. The public contracts are covered end to end, but the core helper paths that assemble ranked summary payloads and redact dropped-line diagnostics are still mostly verified indirectly.
  - DoD:
    - Expand `tests/test_cli_helpers.py` to cover `_top_items(...)` ordering/tie behavior and `_build_incident_summary(...)` for `incident_window`, `event_count`, `error_count`, `top_components`, `top_error_signatures`, `evidence_by_source`, and `correlation_id_coverage` across mixed evidence/non-evidence event sets.
    - Add direct `_redact_parse_summary(...)` coverage proving deterministic placeholder reuse inside diagnostics and no-op behavior when diagnostics are absent.
    - Keep assertions aligned with the documented CLI/README contract rather than incidental dict-construction trivia beyond documented ordering.
  - Verification:
    - `.venv/bin/python -m pytest -q tests/test_cli_helpers.py`
    - `.venv/bin/python -m pytest -q tests/test_summary_contract.py`
    - `.venv/bin/python -m pytest -q tests/test_cli.py -k "summary or redact"`
    - `make test`

- [ ] ITK-031 (P3): Add direct utility-edge coverage for timestamp normalization and correlation-ID extraction helpers
  - Why (impact): `utils.py` is tiny but sits under every parse path. Its current direct test surface is still narrow relative to how much parser behavior depends on it, especially for correlation-ID extraction and timestamp-shape edge cases.
  - DoD:
    - Expand `tests/test_utils.py` to cover `extract_correlation_id(...)` for supported `cid=` / `correlation_id=` message patterns plus clear non-match cases.
    - Add timestamp helper cases for microseconds, naive vs offset-aware inputs, `T` vs space separators, and invalid offset/timestamp shapes.
    - Keep the suite focused on documented helper behavior rather than duplicating end-to-end parser tests wholesale.
  - Verification:
    - `.venv/bin/python -m pytest -q tests/test_utils.py`
    - `.venv/bin/python -m pytest -q tests/test_parser.py -k "timestamp or correlation"`
    - `make test`

---

Recently completed (kept brief so the live queue stays short):

- [x] ITK-030 (P1): Add full redacted golden fixtures for parse diagnostics, timeline, and runbook outputs
- [x] ITK-028 (P1): Add a fixture-driven parity suite proving `summary`, `timeline`, and `runbook` stay aligned on the same filtered incident slice
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
