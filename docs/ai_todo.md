# ai_todo.md (deterministic)

Rule: work ONLY on the **first unchecked top-level** item.

Priority refresh basis: `docs/status.md` + `docs/critical_todo.md` + live repo/doc verification (2026-03-13 UTC):
- `git status --short --branch` ✅ clean on entry to this docs-only maintenance pass (`## main...origin/main`)
- `docs/status.md` ✅ exists
- `docs/critical_todo.md` ✅ exists and is currently empty (`- (none)`)
- `docs/ai_todo.md` ✅ exists
- `docs/deep_research_auto.md` ✅ exists
- `docs/user_todo.md` ✅ exists and has no open checkbox items
- Latest recorded verification in `docs/status.md` remains green:
  - `make lint` ✅
  - `make test` ✅ (`201 passed`)
- Current repo facts from this maintenance pass:
  - `docs/status.md` shows ITK-039, ITK-040, and ITK-041 are complete, so the README-led console-script path plus the known runbook/strict-mode regressions should no longer be in the active queue
  - `docs/status.md` also confirms ITK-038 is complete, so README-advertised `triage summary --out <file>` parity is already locked
  - `tests/test_main.py` now directly proves both `python -m triage_toolkit` and the installed `triage` console script against the same version and missing-file expectations
  - Live `coverage report -m` still shows the largest remaining user-facing branch surface concentrated in `triage_toolkit/runbook.py` and the shared `triage_toolkit/markdown.py` helper, while the remaining parser/CLI misses are thin wrapper seams
  - `docs/critical_todo.md` has no build/security/data-loss emergency queued, so the highest-impact remaining work is operator-facing runbook/markdown fallback coverage first, then tiny helper/entrypoint cleanup

## Open priorities (highest engineering impact first)

- [ ] ITK-042 (P2): Lock runbook empty/no-evidence fallbacks and direct markdown helper behavior
  - Why (impact): `docs/status.md` closed the known pipe/newline/backtick rendering bugs, but the live branch surface still clusters in `runbook.py` and `markdown.py`. Empty/no-evidence runbooks and code-span/text sanitization are operator-facing artifacts, so regressions here create misleading handoff docs even when parsing is correct.
  - DoD:
    - Add focused `build_runbook(...)` coverage for truly empty inputs and for parsed-event slices with no error-like evidence, asserting the explicit Symptoms/Evidence/Checks/Workaround/Fix/Verification fallback text stays stable.
    - Add direct helper coverage for `markdown_safe_text(...)` and `markdown_code_span(...)`, including CR/LF flattening, pipe escaping, optional backtick escaping, leading/trailing space handling, and safe fence widening for embedded backticks.
    - Keep the change narrow to tests unless a real contract bug is exposed.
  - Verification:
    - `.venv/bin/python -m pytest -q tests/test_runbook.py -k "empty or no evidence"`
    - `.venv/bin/python -m pytest -q tests/test_markdown.py`
    - `make test`

- [ ] ITK-036 (P3): Close the remaining thin CLI/parser helper and entrypoint seams so the last uncovered lines are fully intentional
  - Why (impact): once console-script parity and operator-facing runbook fallbacks are locked, the remaining misses are tiny glue. This is low-risk work, but cheap direct coverage here keeps future refactors from regressing edge execution paths that still are not explicitly exercised.
  - DoD:
    - Add helper coverage for `_read_stdin_lines()` when `sys.stdin` has no `.buffer` and for `_read_events_for_parse([])` failing with the stable missing-input message.
    - Add direct wrapper coverage for `parse_file(...)` delegating to `parse_file_with_summary(...)`.
    - Add a module-entrypoint smoke test that exercises the `triage_toolkit.cli` `__main__` path (not just `triage_toolkit.__main__`) so the remaining `cli.py` guard is intentional too.
  - Verification:
    - `.venv/bin/python -m pytest -q tests/test_cli_helpers.py -k "stdin or read_events_for_parse"`
    - `.venv/bin/python -m pytest -q tests/test_parser.py -k "parse_file"`
    - `.venv/bin/python -m pytest -q tests/test_main.py -k "cli or main or module"`
    - `make test`

---

Recently completed (kept brief so the live queue stays short):

- [x] ITK-039 (P1): Lock installed `triage` console-script parity with the documented quickstart
- [x] ITK-040 (P1): Harden remaining markdown/code-span safety for runbook titles and backtick-heavy dynamic fields
- [x] ITK-041 (P1): Prove strict parse-gate failures never create or overwrite output files
- [x] ITK-038 (P1): Restore README quickstart/write-path parity by locking `triage summary --out <file>` at the CLI contract layer
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
