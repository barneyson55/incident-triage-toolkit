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
  - `.venv/bin/python -m pytest --cov=triage_toolkit --cov-report=term-missing -q` ✅ (`186 passed`, total coverage `99%`)
  - current uncovered lines are limited to `triage_toolkit/cli.py:102,148,264,397,522` and `triage_toolkit/parser.py:265-266`
  - focused repo search confirms direct parser alias coverage now exists, while no focused tests currently lock markdown-safety edge cases around pipe/newline handling across all operator-facing dynamic fields
- Current repo facts from this maintenance pass:
  - the package remains intentionally compact and layered: `parser.py` + `utils.py` ingest, `cli.py` owns operator-facing command flow and strict gates, `evidence.py` + `redaction.py` provide shared semantics, and `timeline.py` / `runbook.py` render operator-facing markdown
  - repo footprint remains small enough for coverage-first hardening: 10 source modules, 11 top-level test modules, a single runtime dependency (`typer==0.21.1`), and a currently green 186-test suite
  - dedicated contract/golden coverage already exists for parse, summary, timeline, and runbook surfaces, including redacted goldens, alias-heavy JSON fixtures, and cross-surface parity coverage
  - repo evidence now points to a more specific operator-surface risk than raw coverage percentage alone: `timeline.py` escapes markdown pipes for `source` and `message`, but not for `component`, while JSON-line ingestion can still supply arbitrary string values for component-like alias fields
  - `timeline.py` and `runbook.py` flatten message newlines in some rendered paths, but there is still no focused contract coverage proving all operator-facing dynamic strings stay single-line and markdown-safe when inputs contain embedded newlines or literal `|`
  - after those operator-facing gaps, the remaining blind spots are truly thin wrapper/helper paths: `_read_stdin_lines()` without `.buffer`, `_read_events_for_parse([])`, no-filter passthrough in `_apply_event_filters(...)`, the summary file-success path, script/module entrypoint glue in `cli.py`, and `parse_file(...)`

## Open priorities (highest engineering impact first)

- [x] ITK-034 (P1): Harden operator-facing markdown rendering against pipe/newline corruption in timeline and runbook output
  - Why (impact): the repo is already at 99% coverage, so the highest remaining risk is no longer parser correctness but handoff quality. Timeline/runbook output is what humans read under pressure, and GFM-style tables require escaped pipes plus single-line cell content. Repo evidence shows `timeline.py` currently escapes `source` and `message`, but not `component`, even though JSON ingestion can feed arbitrary component strings.
  - DoD:
    - Add focused timeline coverage proving `source`, `component`, and `message` cells render safely when input contains literal `|` characters or embedded newlines.
    - Add focused runbook coverage proving evidence/example/source-summary rendering keeps dynamic strings on a single line and does not corrupt bullet structure when upstream values contain embedded newlines.
    - Fix renderer helpers as needed, preferring one small shared markdown-safety helper over repeated ad hoc escaping.
    - Keep explicit provenance fallback assertions where rendered surfaces should still show `n/a` when no source metadata is available.
  - Verification:
    - `.venv/bin/python -m pytest -q tests/test_timeline.py -k "pipe or newline or markdown or source"`
    - `.venv/bin/python -m pytest -q tests/test_runbook.py -k "newline or markdown or source"`
    - `make test`

- [ ] ITK-038 (P2): Restore README quickstart/write-path parity by locking `triage summary --out <file>` at the CLI contract layer
  - Why (impact): README quickstart examples advertise file-output workflows for all four commands, and parse/timeline/runbook already have write-path success coverage. `summary` is the remaining user-visible gap, and it corresponds directly to one of the still-uncovered `cli.py` branches.
  - DoD:
    - Add a CLI test proving `triage summary <input> --out <file>` writes the JSON file and emits the stable success message.
    - Assert the written payload preserves the documented machine-readable contract (`schema_version`, incident window, and raw `parse_summary`) rather than only checking that a file exists.
    - Keep the test narrow and fixture-light so it closes the quickstart gap without broad contract churn.
  - Verification:
    - `.venv/bin/python -m pytest -q tests/test_cli.py -k "summary and out"`
    - `make test`

- [ ] ITK-036 (P3): Close the remaining thin helper/wrapper seams so the last uncovered lines are fully intentional
  - Why (impact): once the operator-facing markdown and quickstart write-path gaps are locked, the only remaining uncovered code is tiny glue. It is low-risk work, but cheap coverage here keeps future refactors from regressing edge execution paths that still are not directly exercised.
  - DoD:
    - Add helper coverage for `_read_stdin_lines()` when `sys.stdin` has no `.buffer`, `_read_events_for_parse([])` failing deterministically, and `_apply_event_filters(...)` returning the full ordered input when no filters are supplied.
    - Add direct wrapper coverage for `parse_file(...)` delegating to `parse_file_with_summary(...)`.
    - Add a script/module entrypoint smoke test that exercises the `triage_toolkit.cli` `__main__` path (not just `triage_toolkit.__main__`) so the remaining `cli.py` entrypoint line is intentional too.
  - Verification:
    - `.venv/bin/python -m pytest -q tests/test_cli_helpers.py -k "stdin or read_events_for_parse or filters"`
    - `.venv/bin/python -m pytest -q tests/test_parser.py -k "parse_file"`
    - `.venv/bin/python -m pytest -q tests/test_main.py -k "cli or main or module"`
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
