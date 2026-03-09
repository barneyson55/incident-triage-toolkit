# ai_todo.md (deterministic)

Rule: work ONLY on the **first unchecked top-level** item.

Priority refresh basis: `docs/status.md` + `docs/critical_todo.md` + current repo verification (2026-03-09 15:58 UTC):
- `docs/status.md` ✅ current enough on the main product direction: ITK-018 is complete, and evidence-driven runbook output (ITK-017) is now the next highest-impact product gap.
- `README.md` ✅ documents both deterministic filter parity and stdin ingestion semantics.
- `docs/critical_todo.md` ✅ no open critical items.
- `docs/user_todo.md` ✅ no open manual-user blockers.
- `make test` ✅ (85 passed)

## Open priorities (highest engineering impact first)

- [x] ITK-016 (P1): Finish deterministic incident-slicing filter parity for `timeline` and `runbook`
  - Why (impact): this is the most immediate product gap because the repo already shipped `summary` filters, but operators still cannot carry the same slice into human-readable outputs. That forces context switching and weakens the “one incident slice, all outputs” workflow.
  - DoD:
    - Add repeated `--component`, `--level`, and `--correlation-id` flags to `timeline` and `runbook`.
    - Repeating the same flag widens with OR semantics; different filter families combine with AND semantics, matching the existing `summary` contract.
    - Filtered `timeline`/`runbook` outputs preserve deterministic event ordering.
    - Strict parse gates and parse-quality summaries continue to evaluate the raw ingested inputs before filtering, so filters cannot hide parse failures.
    - README examples and filter-semantics docs cover all three commands consistently.
  - Verification:
    - `pytest -q tests/test_cli.py -k "filter and timeline or filter and runbook"`
    - `pytest -q tests/test_timeline.py -k "filter"`
    - `pytest -q tests/test_runbook.py -k "filter"`
    - `make test`

- [x] ITK-018 (P1): Support stdin ingestion (`-`) across CLI commands
  - Why (impact): after filter parity, the highest workflow leverage is shell-native input. A line-oriented incident CLI should work naturally with `kubectl logs`, `journalctl`, pasted snippets, and pipeline preprocessing instead of requiring temp files.
  - DoD:
    - `parse`, `summary`, `timeline`, and `runbook` accept `-` as a UTF-8 stdin source.
    - Mixing rules are explicit and deterministic (stdin allowed at most once, stable source labeling, documented merge ordering when files and stdin are combined).
    - Strict parse behavior, multi-input merge semantics, and parse summaries remain correct when stdin participates.
    - README documents stdin examples for Linux/macOS/WSL and notes any PowerShell caveats.
  - Verification:
    - `pytest -q tests/test_cli.py -k "stdin or standard_input"`
    - `pytest -q tests/test_parser.py -k "stream or stdin"`
    - `make test`

- [ ] ITK-017 (P2): Make runbook output evidence-driven instead of mostly boilerplate
  - Why (impact): the current runbook is deterministic and usable, but it still reads more like a template than a strong handoff artifact. Once filter parity is complete, the runbook should surface real incident evidence rather than generic placeholders.
  - DoD:
    - Add deterministic evidence sections derived from parsed events (for example: incident window, top error signatures, suspected components with counts, representative correlation IDs, or example failures).
    - Keep timestamps UTC-first and ordering deterministic.
    - Reuse existing summary/filter logic where practical so markdown output does not fork incident-analysis rules.
    - Update golden fixtures/tests to lock the richer markdown contract.
    - README documents the upgraded runbook structure and any filtering interaction.
  - Verification:
    - `pytest -q tests/test_runbook.py -k "golden or evidence or signature"`
    - `pytest -q tests/test_cli.py -k "runbook and golden"`
    - `make test`

---

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
