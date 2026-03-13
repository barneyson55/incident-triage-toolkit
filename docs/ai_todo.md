# ai_todo.md (deterministic)

Rule: work ONLY on the **first unchecked top-level** item.

Priority refresh basis: `docs/status.md` + `docs/critical_todo.md` + live repo/doc verification (2026-03-13 UTC):
- `git status --short --branch` ✅ clean on entry to this docs-only maintenance pass (`## main...origin/main`)
- `docs/status.md` ✅ exists
- `docs/critical_todo.md` ✅ exists
- `docs/ai_todo.md` ✅ exists
- `docs/deep_research_auto.md` ✅ exists
- `docs/user_todo.md` ✅ exists and has no open checkbox items
- Live verification from this maintenance pass:
  - `.venv/bin/python -m pytest --cov=triage_toolkit --cov-report=term-missing -q` ✅ (`186 passed`, total coverage `99%`; remaining uncovered lines are isolated to thin branches in `triage_toolkit/cli.py` and `triage_toolkit/parser.py`)
  - focused repo search confirms direct parser alias tests now exist in `tests/test_parser.py`, while no focused `timeline` / `runbook` pipe/newline assertions or thin-wrapper tests for `_read_stdin_lines()`, `_read_events_for_parse([])`, `parse_file(...)`, and `main()` were found
- Current repo facts from this maintenance pass:
  - the package remains intentionally compact and layered: `parser.py` + `utils.py` ingest, `cli.py` owns operator-facing command flow and strict gates, `evidence.py` + `redaction.py` provide shared semantics, and `timeline.py` / `runbook.py` render operator-facing markdown
  - repo footprint remains small enough for coverage-first hardening: 10 source modules, 11 top-level test modules, 19 tracked fixture files under `tests/fixtures/`, and a currently green collected suite at 186 tests
  - dedicated helper suites already exist for shared CLI plumbing, evidence logic, and redaction behavior (`tests/test_cli_helpers.py`, `tests/test_evidence.py`, `tests/test_redaction.py`)
  - dedicated contract/golden coverage already exists for parse, summary, timeline, and runbook surfaces, including redacted goldens and cross-surface parity coverage
  - direct parser coverage now locks heterogeneous JSON aliases and correlation-ID precedence in `tests/test_parser.py`, and the public CLI contract now adds a compact alias-heavy end-to-end fixture spanning `parse`, `summary`, `timeline`, and `runbook`
  - `timeline.py` and `runbook.py` still have no focused coverage for markdown-formatting edge cases like pipe escaping in table cells or newline flattening in rendered operator-facing messages
  - live coverage now narrows the remaining low-level blind spots to wrapper/helper branches such as `_read_stdin_lines()`, `_read_events_for_parse([])`, no-filter passthrough in `_apply_event_filters(...)`, the summary file-success path, `main()`, and `parse_file(...)`

## Open priorities (highest engineering impact first)

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

- [ ] ITK-036 (P4): Close the remaining thin wrapper/helper branch gaps revealed by the current 99% coverage report
  - Why (impact): after the semantic gaps above, the remaining uncovered lines are concentrated in tiny CLI/parser wrappers. Locking them is low-risk and keeps future refactors from regressing seemingly trivial operator paths that the suite still does not directly exercise.
  - DoD:
    - Add helper coverage for `_read_stdin_lines()` when `sys.stdin` has no `.buffer`, `_read_events_for_parse([])` failing deterministically, and `_apply_event_filters(...)` returning the full ordered input when no filters are supplied.
    - Add direct wrapper coverage for `parse_file(...)` delegating to `parse_file_with_summary(...)` and `main()` delegating to `app()`.
    - Add one command-level test proving `triage summary <input> --out <file>` writes the file and emits the success message, so the remaining summary file-output branch is no longer implicit.
  - Verification:
    - `.venv/bin/python -m pytest -q tests/test_cli_helpers.py -k "stdin or read_events_for_parse or filters"`
    - `.venv/bin/python -m pytest -q tests/test_parser.py -k "parse_file"`
    - `.venv/bin/python -m pytest -q tests/test_main.py tests/test_cli.py -k "summary or main"`
    - `make test`

---

Recently completed (kept brief so the live queue stays short):

- [x] ITK-037 (P2): Add a compact end-to-end CLI contract fixture for alias-shaped JSON logs
- [x] ITK-035 (P2): Lock heterogeneous JSON-ingestion aliases and correlation-ID precedence with direct parser coverage
- [x] ITK-031 (P2): Add direct utility-edge coverage for timestamp normalization and correlation-ID extraction helpers
- [x] ITK-033 (P2): Close the remaining direct CLI operator-surface coverage gaps for file-summary/stdin failure paths and entrypoint behavior
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
