# ai_todo.md (deterministic)

Rule: work ONLY on the **first unchecked top-level** item.

Priority refresh basis: `docs/status.md` + `docs/critical_todo.md` + live repo/doc verification (2026-03-13 UTC):
- `git status --short --branch` ✅ clean on entry to this docs-only maintenance pass (`## main...origin/main`)
- `docs/status.md` ✅ exists
- `docs/critical_todo.md` ✅ exists and is currently empty (`- (none)`)
- `docs/ai_todo.md` ✅ exists
- `docs/deep_research_auto.md` ✅ exists
- `docs/user_todo.md` ✅ exists and has no open checkbox items
- Live verification from this maintenance pass:
  - `.venv/bin/python -m pytest --cov=triage_toolkit --cov-report=term-missing -q` ✅ (`188 passed`, total coverage `99%`)
  - current uncovered lines are limited to `triage_toolkit/cli.py:102,148,264,397,522` and `triage_toolkit/parser.py:265-266`
- Current repo facts from this maintenance pass:
  - operator-facing pipe/newline markdown hardening is complete and already reflected in `docs/status.md` (`triage_toolkit/markdown.py` plus focused timeline/runbook regressions)
  - the codebase remains intentionally compact: 10 source modules, 11 top-level test modules, one direct runtime dependency (`typer==0.21.1`), and a fully green suite
  - parse, summary, timeline, runbook, redaction, parity, and alias-heavy ingestion contracts are already covered directly, so the remaining high-value work is now concentrated on user-visible CLI seams rather than parser fundamentals
  - README quickstart still advertises both file-output workflows and the installed `triage` console script, but current direct coverage is still stronger for stdout/module-entrypoint flows than for every documented write/entrypoint path
  - strict parse gates are covered for failure signaling, but there is still no focused contract proving failed strict runs leave file outputs absent/untouched instead of accidentally creating misleading artifacts
  - after those user-facing seams, the last uncovered code is truly thin glue only: `_read_stdin_lines()` without `.buffer`, `_read_events_for_parse([])`, correlation-ID filter passthrough in `_apply_event_filters(...)`, the summary file-success echo path, the `triage_toolkit.cli` script entrypoint, and `parse_file(...)`

## Open priorities (highest engineering impact first)

- [x] ITK-038 (P1): Restore README quickstart/write-path parity by locking `triage summary --out <file>` at the CLI contract layer
  - Why (impact): README quickstart examples advertise file-output workflows for all four commands, and parse/timeline/runbook already have stronger write-path coverage. `summary` is the remaining user-visible gap, and it maps directly to one of the still-uncovered `cli.py` lines.
  - DoD:
    - Add a CLI test proving `triage summary <input> --out <file>` writes the JSON file and emits the stable success message.
    - Assert the written payload preserves the documented machine-readable contract (`schema_version`, incident window, top lists, and raw `parse_summary`) rather than only checking that a file exists.
    - Keep the test narrow and fixture-light so it closes the quickstart gap without broad contract churn.
  - Verification:
    - `.venv/bin/python -m pytest -q tests/test_cli.py -k "summary and out"`
    - `.venv/bin/python -m pytest -q tests/test_summary_contract.py -k "summary"`
    - `make test`

- [ ] ITK-040 (P1): Harden remaining markdown/code-span safety for runbook titles and backtick-heavy dynamic fields
  - Why (impact): pipe/newline corruption is fixed, but `runbook.py` still renders several dynamic values inside inline-code spans and a raw H1 title. Literal backticks or embedded newlines in titles, signatures, correlation IDs, or source labels can still degrade the handoff artifact even when the underlying incident logic is correct.
  - DoD:
    - Add focused runbook coverage for titles containing embedded newlines or literal backticks, and for dynamic values rendered inside backticks (for example correlation IDs, source labels, and top signatures).
    - Introduce the smallest shared markdown-safety adjustment needed so operator-facing runbook output stays readable and single-line where intended.
    - Preserve the current explicit `n/a` provenance fallback and avoid broad markdown/golden churn outside the newly proven edge cases.
  - Verification:
    - `.venv/bin/python -m pytest -q tests/test_runbook.py -k "title or backtick or markdown or source"`
    - `.venv/bin/python -m pytest -q tests/test_cli.py -k "runbook"`
    - `make test`

- [ ] ITK-039 (P2): Lock installed `triage` console-script parity with the documented quickstart
  - Why (impact): the package metadata defines `triage = triage_toolkit.cli:main`, and README quickstart leads with `triage ...` commands, but current direct subprocess coverage exercises `python -m triage_toolkit` rather than the installed script wrapper. A broken console-script entrypoint would hurt first-run UX while still leaving most tests green.
  - DoD:
    - Add one focused subprocess smoke test for the installed `triage` command (for example `triage --version`) and one narrow command-path assertion (for example parse stdout or missing-file error behavior).
    - Keep the test resilient to the active virtualenv/dev-install layout instead of hardcoding an environment-specific script path.
    - Reuse existing version/error expectations so this stays an entrypoint-parity task, not a new CLI-contract expansion.
  - Verification:
    - `.venv/bin/python -m pytest -q tests/test_main.py -k "triage or console or version"`
    - `make test`

- [ ] ITK-041 (P2): Prove strict parse-gate failures never create or overwrite output files
  - Why (impact): strict mode is meant to fail fast when parse quality is too poor. The error messaging is covered already, but there is no focused file-safety regression test proving `--strict --out <file>` does not leave behind fresh or overwritten artifacts that could be mistaken for valid outputs.
  - DoD:
    - Add narrow CLI tests for `parse`, `summary`, `timeline`, and `runbook` using failing strict inputs with file outputs.
    - Assert exit code `2`, stable strict-gate error fragments, and that the output file is either absent or unchanged from a pre-existing sentinel value.
    - Keep the task at the contract level only; no product behavior change is needed unless the tests expose a bug.
  - Verification:
    - `.venv/bin/python -m pytest -q tests/test_cli.py -k "strict and out"`
    - `make test`

- [ ] ITK-036 (P3): Close the remaining thin helper/wrapper seams so the last uncovered lines are fully intentional
  - Why (impact): once the user-visible write/markdown/entrypoint/file-safety seams are locked, the only remaining uncovered code is tiny glue. It is low-risk work, but cheap coverage here keeps future refactors from regressing edge execution paths that still are not directly exercised.
  - DoD:
    - Add helper coverage for `_read_stdin_lines()` when `sys.stdin` has no `.buffer`, `_read_events_for_parse([])` failing deterministically, and `_apply_event_filters(...)` rejecting non-matching correlation IDs while returning the full ordered input when no filters are supplied.
    - Add direct wrapper coverage for `parse_file(...)` delegating to `parse_file_with_summary(...)`.
    - Add a script/module entrypoint smoke test that exercises the `triage_toolkit.cli` `__main__` path (not just `triage_toolkit.__main__`) so the remaining `cli.py` entrypoint line is intentional too.
  - Verification:
    - `.venv/bin/python -m pytest -q tests/test_cli_helpers.py -k "stdin or read_events_for_parse or filters"`
    - `.venv/bin/python -m pytest -q tests/test_parser.py -k "parse_file"`
    - `.venv/bin/python -m pytest -q tests/test_main.py -k "cli or main or module"`
    - `make test`

---

Recently completed (kept brief so the live queue stays short):

- [x] ITK-034 (P1): Harden operator-facing markdown rendering against pipe/newline corruption in timeline and runbook output
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
