# ai_todo.md (deterministic)

Rule: work ONLY on the **first unchecked top-level** item.

Priority refresh basis: `docs/status.md` + `docs/critical_todo.md` + current repo verification (2026-03-09 08:41 UTC):
- `docs/status.md` ⚠️ reviewed, but stale versus the current working tree: it still points to older next steps, while local CLI/README/test changes show ITK-014 is already implemented and passing.
- `docs/critical_todo.md` ✅ no open critical items.
- `git status --short` ⚠️ working tree not clean; active non-doc edits already exist in `README.md`, `tests/test_cli.py`, and `triage_toolkit/cli.py`.
- `make test` ✅ (65 passed)
- `.venv/bin/python -m pytest -q tests/test_cli.py -k "summary and multiple_inputs"` ✅ (3 passed)
- `.venv/bin/python -m pytest --cov=triage_toolkit --cov-report=term-missing --cov-fail-under=88` ✅ (98.01%)

## Open priorities (highest engineering impact first)

- [ ] ITK-015 (P1): Add deterministic dropped-line diagnostics for parse quality investigation
  - Why (impact): strict parse gates now prevent silent data loss, but they still do a poor job of explaining failures. When drop ratio spikes, operators cannot yet see which exact lines were rejected, which slows parser debugging and weakens trust in the toolkit.
  - DoD:
    - Add a bounded diagnostics surface for dropped lines (opt-in output field or dedicated command/option).
    - Each diagnostic entry includes at least: source path, line number, drop reason, and raw sample line.
    - Ordering/sampling is deterministic across runs and explicitly documented.
    - Any new machine-readable contract follows the existing schema-version discipline.
    - README documents how to use diagnostics during triage and what limits/redaction assumptions apply.
  - Verification:
    - `pytest -q tests/test_parser.py -k "dropped and diagnostics"`
    - `pytest -q tests/test_cli.py -k "strict and diagnostics or dropped_examples"`
    - `make test`

- [ ] ITK-016 (P1): Add deterministic incident-slicing filters for noisy logs
  - Why (impact): the current CLI always processes the full event set. Real incident work often needs fast slices by component, level, or correlation ID without forcing operators into ad-hoc `grep`/`jq` chains.
  - DoD:
    - Add repeated filters such as `--component`, `--level`, and `--correlation-id` to `summary`, `timeline`, and `runbook`.
    - Filtered outputs preserve deterministic event ordering and deterministic top-list ordering.
    - Strict parse gates continue to evaluate raw ingestion quality rather than the filtered subset, so filters cannot hide parse failures.
    - README documents filter semantics, repeated-flag behavior, and examples.
  - Verification:
    - `pytest -q tests/test_cli.py -k "filter and summary or filter and timeline or filter and runbook"`
    - `pytest -q tests/test_timeline.py -k "filter"`
    - `pytest -q tests/test_runbook.py -k "filter"`
    - `make test`

- [ ] ITK-018 (P1): Support stdin ingestion (`-`) across CLI commands
  - Why (impact): the toolkit already supports stdout (`--out -`) but not stdin input. For a line-oriented incident CLI, that blocks high-value shell-native workflows like `kubectl logs`, `journalctl`, pasted snippets, and pipe-based preprocessing.
  - DoD:
    - `parse`, `summary`, `timeline`, and `runbook` accept `-` as a UTF-8 stdin source.
    - Mixing rules are explicitly defined and deterministic (for example: stdin allowed at most once, source label is stable, multi-input ordering stays documented).
    - Strict parse behavior and multi-input merge semantics remain correct when stdin participates.
    - README documents stdin examples for Linux/macOS/WSL.
  - Verification:
    - `pytest -q tests/test_cli.py -k "stdin or standard_input"`
    - `pytest -q tests/test_parser.py -k "stream"`
    - `make test`

- [ ] ITK-017 (P2): Make runbook output evidence-driven instead of mostly boilerplate
  - Why (impact): current runbook output is stable but still closer to a template than a strong handoff artifact. The repo already has enough structured incident data to make the runbook materially more useful without adding dependencies.
  - DoD:
    - Add deterministic evidence sections derived from parsed events (for example: incident window, top error signatures, suspected components with counts, representative correlation IDs, or example failures).
    - Keep timestamps UTC-first and ordering deterministic.
    - Reuse existing summary/filter logic where practical so markdown output does not fork incident-analysis rules.
    - Update golden fixtures/tests to lock the richer markdown contract.
    - README documents the upgraded runbook structure.
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
