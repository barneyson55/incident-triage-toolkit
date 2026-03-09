# ai_todo.md (deterministic)

Rule: work ONLY on the **first unchecked top-level** item.

Priority refresh basis: `docs/status.md` + `docs/critical_todo.md` + current repo verification (2026-03-09 18:3x UTC):
- `make test` ✅ (91 passed)
- `docs/status.md` ✅ updated for ITK-019 completion and the next provenance/redaction gaps.
- `README.md` ✅ documents multi-input ingestion, deterministic merge order, output filters, stdin ingestion, dropped-line diagnostics, richer runbook evidence structure, and the canonical shared evidence-classification rules.
- `docs/critical_todo.md` ✅ no open critical items.
- Code review gaps now matter more than the closed evidence-semantics issue:
  - `triage_toolkit/models.py` and the parse JSON contract do not preserve `source_path` / source line number for successfully parsed events, so multi-input evidence is still hard to trace back to the original log line.
  - Timeline rows and runbook evidence snippets therefore still cannot cite the original source file/stdin label and line number.
  - Dropped-line diagnostics already expose raw rejected text. Richer evidence excerpts now exist in runbooks too, so the toolkit needs a deterministic safe-sharing path rather than relying only on upstream manual scrubbing.

## Open priorities (highest engineering impact first)

- [x] ITK-017 (P1): Make runbook output evidence-driven instead of mostly boilerplate
  - Why (impact): the core parser/summary/timeline pipeline is now stable, but the runbook still reads like a generic template instead of a strong incident handoff artifact. This is the biggest remaining product gap on the human-facing output surface.
  - DoD:
    - Add deterministic evidence sections derived from parsed events (for example: incident window, top error signatures, suspected components with counts, representative correlation IDs, and 1-3 example failures).
    - Example failures are chosen deterministically (for example: earliest occurrence per top signature) and remain UTC-first.
    - Empty/filter-miss runbooks keep a stable explicit no-evidence template instead of generic filler.
    - Reuse shared summary/evidence helpers where practical so markdown output does not fork incident-analysis rules.
    - Update golden fixtures/tests to lock the richer markdown contract.
    - README documents the upgraded runbook structure and how filters affect evidence sections.
  - Verification:
    - `pytest -q tests/test_runbook.py -k "golden or evidence or example or signature"`
    - `pytest -q tests/test_cli.py -k "runbook and (golden or filter or strict)"`
    - `make test`

- [x] ITK-019 (P1): Unify incident evidence semantics across `summary`, `timeline`, and `runbook`
  - Why (impact): the current repo can disagree with itself about what counts as an error/evidence event. That weakens operator trust, especially once runbook evidence gets richer.
  - Done:
    - Shared evidence helpers now drive `summary.error_count`, `summary.top_error_signatures`, timeline `Notable Errors`, and runbook evidence/symptom sections.
    - Added explicit parity coverage for `ERROR`, `CRITICAL`, `FATAL`, and message-based `error` hints.
    - Made signature/component tie-break ordering explicit and deterministic.
    - README now documents the canonical evidence/error classification rules.
  - Verification:
    - `pytest -q tests/test_cli.py -k "summary and (critical or fatal or error)"`
    - `pytest -q tests/test_timeline.py -k "critical or fatal or error"`
    - `pytest -q tests/test_runbook.py -k "critical or fatal or error"`
    - `make test`

- [ ] ITK-020 (P1): Preserve source provenance for successful parsed events and rendered evidence
  - Why (impact): multi-input support is already shipped, but successful events still lose the exact source file / stdin label and line number. That makes operator handoff, auditability, and incident debugging weaker than they should be.
  - DoD:
    - Extend the parsed event contract with deterministic source provenance for successful events (source label/path and original line number), with an explicit schema-version update.
    - Preserve the stable stdin source label `-` and multi-input merge semantics.
    - Surface provenance in timeline rows and runbook evidence excerpts in a concise, readable format.
    - Keep strict parse gates and event ordering unchanged.
    - Update README and golden fixtures/tests for the new provenance contract.
  - Verification:
    - `pytest -q tests/test_parser.py -k "source and line"`
    - `pytest -q tests/test_cli.py -k "parse and provenance"`
    - `pytest -q tests/test_timeline.py -k "provenance"`
    - `pytest -q tests/test_runbook.py -k "provenance"`
    - `make test`

- [ ] ITK-021 (P2): Add deterministic redaction controls for diagnostics and evidence surfaces
  - Why (impact): dropped-line diagnostics and richer evidence snippets are valuable, but they are risky to share as-is. A safe-sharing mode would make the toolkit more usable in real support handoff workflows.
  - DoD:
    - Add an opt-in redaction mode for dropped-line diagnostics and runbook evidence snippets.
    - Redaction is deterministic and uses stable placeholders for at least emails, IP addresses, UUID/correlation-style identifiers, and long token-like secrets.
    - Redaction happens after parse-quality evaluation, so strict parse behavior and counters do not change.
    - README documents the exact placeholder policy and the limits of the built-in redaction.
    - Regression tests prove identical input produces identical redacted output across parse/runbook paths.
  - Verification:
    - `pytest -q tests/test_cli.py -k "redact or diagnostics"`
    - `pytest -q tests/test_runbook.py -k "redact or evidence"`
    - `make test`

---

Recently completed (kept brief so the live queue stays short):

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
