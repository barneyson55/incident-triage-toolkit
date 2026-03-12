# ai_todo.md (deterministic)

Rule: work ONLY on the **first unchecked top-level** item.

Priority refresh basis: `docs/status.md` + `docs/critical_todo.md` + live repo/doc verification (2026-03-12 UTC):
- `git status --short --branch` ✅ clean on entry to this docs-only maintenance pass (`## main...origin/main`)
- `docs/status.md` ✅ exists
- `docs/critical_todo.md` ✅ exists
- `docs/ai_todo.md` ✅ exists
- `docs/deep_research_auto.md` ✅ exists
- `docs/user_todo.md` ✅ exists and has no open checkbox items
- Current repo facts from this maintenance pass:
  - the package remains intentionally compact and layered: `parser.py` + `utils.py` ingest, `cli.py` owns operator-facing command flow and strict gates, `evidence.py` + `redaction.py` provide shared semantics, and `timeline.py` / `runbook.py` render operator-facing markdown
  - repo footprint remains small enough for coverage-first hardening: 10 source modules, 11 top-level test modules, 142 top-level test functions, and 18 tracked fixture files under `tests/fixtures/`
  - dedicated helper suites already exist for shared CLI plumbing, evidence logic, and redaction behavior (`tests/test_cli_helpers.py`, `tests/test_evidence.py`, `tests/test_redaction.py`)
  - dedicated contract/golden coverage already exists for parse, summary, timeline, and runbook surfaces, including redacted goldens and cross-surface parity coverage
  - `tests/test_main.py` now covers both the monkeypatched `__main__` wire-up and direct `python -m triage_toolkit` subprocess behavior for `--version` plus a stable missing-file failure path
  - `tests/test_utils.py` still has only five direct tests and no direct `extract_correlation_id(...)` coverage
  - `tests/test_cli.py` still covers `_get_version()`, `--version`, and broader operator-facing input/stdin paths, while `tests/test_cli_helpers.py` now directly locks `_read_events_with_summary(...)` and `_read_events_from_stdin(...)` call-shape/error mapping behavior
  - `timeline.py` and `runbook.py` still have no focused coverage for markdown-formatting edge cases like pipe escaping in table cells or newline flattening in rendered operator-facing messages
  - latest recorded verification in `docs/status.md` is `make test` ✅ (`153 passed`)

## Open priorities (highest engineering impact first)

- [x] ITK-033 (P2): Close the remaining direct CLI operator-surface coverage gaps for file-summary/stdin failure paths and entrypoint behavior
  - Why (impact): the CLI is still the only operator interface. The repo already has direct coverage for `_get_version()`, `--version`, and `_read_events(...)`, but the file-summary and stdin helper paths in `cli.py` still rely more on indirect command coverage than on focused helper assertions, and `tests/test_main.py` is still barely more than a smoke wire-up.
  - DoD:
    - Add direct helper tests for `_read_events_with_summary(...)` covering missing files, unreadable paths, directory inputs, invalid UTF-8, generic `OSError`, and the `diagnostics_limit` branching behavior.
    - Add direct helper tests for `_read_events_from_stdin(...)` covering UTF-8 failure messaging plus `source_order` / `diagnostics_limit` passthrough into `parse_lines_with_summary(...)`.
    - Broaden `tests/test_main.py` beyond pure module-entrypoint smoke so the `python -m triage_toolkit` surface stays distinct from lower-level helper tests and does not silently regress.
    - Keep assertions on stable message fragments, exit behavior, and helper call shape rather than Typer internals or platform-specific errno wording.
  - Verification:
    - `.venv/bin/python -m pytest -q tests/test_main.py`
    - `.venv/bin/python -m pytest -q tests/test_cli_helpers.py -k "read_events_with_summary or read_events_from_stdin"`
    - `.venv/bin/python -m pytest -q tests/test_cli.py -k "version or input or stdin"`
    - `make test`

- [ ] ITK-031 (P3): Add direct utility-edge coverage for timestamp normalization and correlation-ID extraction helpers
  - Why (impact): `utils.py` is tiny but sits under every parse path. Its direct test surface is still much smaller than the parser stack depends on indirectly, especially for supported correlation-ID patterns and timestamp-shape edges.
  - DoD:
    - Expand `tests/test_utils.py` to cover `extract_correlation_id(...)` for supported `cid=` / `correlation_id=` message patterns plus clear non-match cases.
    - Add timestamp helper cases for microseconds, naive vs offset-aware inputs, `T` vs space separators, trailing `Z`, and invalid offset/timestamp shapes.
    - Keep the suite focused on documented helper behavior rather than rebuilding parser end-to-end tests from below.
  - Verification:
    - `.venv/bin/python -m pytest -q tests/test_utils.py`
    - `.venv/bin/python -m pytest -q tests/test_parser.py -k "timestamp or correlation"`
    - `make test`

- [ ] ITK-034 (P3): Add focused markdown-renderer edge coverage for timeline/runbook safety and readability
  - Why (impact): the human-facing timeline and runbook outputs are already covered by happy-path and golden tests, but they still lack targeted assertions for formatting edge cases that can quietly degrade operator handoff quality, especially messages containing pipe characters or embedded newlines.
  - DoD:
    - Add timeline coverage proving event/source cells escape literal `|` characters so markdown tables do not corrupt on real log messages or unusual source labels.
    - Add timeline and runbook coverage proving embedded newlines are flattened to single-line rendered messages/examples instead of breaking table rows or bullet structure.
    - Keep provenance fallback assertions explicit where rendered surfaces should still show `n/a` when no source metadata is available.
    - Prefer narrow rendered-fragment assertions over unrelated full-golden rewrites.
  - Verification:
    - `.venv/bin/python -m pytest -q tests/test_timeline.py -k "pipe or newline or source"`
    - `.venv/bin/python -m pytest -q tests/test_runbook.py -k "newline or source"`
    - `make test`

---

Recently completed (kept brief so the live queue stays short):

- [x] ITK-032 (P2): Add direct CLI summary/redaction helper coverage for automation-facing ordering invariants
- [x] ITK-029 (P2): Tighten parser helper coverage for provenance extraction, diagnostics builders, and source-order propagation
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
