# ai_todo.md (deterministic)

Rule: work ONLY on the **first unchecked top-level** item.

Priority refresh basis: `docs/status.md` + `docs/critical_todo.md` + live repo verification (2026-03-09 18:34 UTC):
- `git status --short --branch` ✅ clean `main...origin/main`
- `make test` ✅ (91 passed)
- `docs/status.md` ✅ updated for ITK-019 completion and the next provenance/redaction gaps.
- `docs/critical_todo.md` ✅ no open critical items.
- Highest-leverage remaining gaps after ITK-019:
  - successful parsed events still do **not** preserve source label/path + original line number
  - timeline/runbook evidence cannot cite the original source line yet
  - diagnostics/evidence still lack a deterministic safe-sharing/redaction mode
  - multi-input support exists, but the outputs still do not show **which source** dominates the evidence slice
  - determinism for equal-timestamp events is still partly implicit outside the CLI merge path
  - the summary JSON automation surface still lacks dedicated contract/golden coverage before the next schema/output expansion

## Open priorities (highest engineering impact first)

- [ ] ITK-020 (P1): Preserve source provenance for successful parsed events and rendered evidence
  - Why (impact): multi-input support is already shipped, but successful events still lose the exact source file / stdin label and line number. That weakens operator handoff, auditability, and root-cause traceability.
  - DoD:
    - Extend the parsed event contract with deterministic source provenance for successful events (`source_path`/label and original `line_number`) with an explicit parse schema-version bump.
    - Preserve the stable stdin label `-` and current multi-input merge semantics.
    - Surface provenance in timeline rows and runbook evidence/example sections in a concise readable form.
    - Keep strict parse gates, evidence semantics, and event ordering unchanged.
    - Update README and regression fixtures/tests for the new provenance contract.
  - Verification:
    - `pytest -q tests/test_parser.py -k "source and line"`
    - `pytest -q tests/test_cli.py -k "parse and provenance"`
    - `pytest -q tests/test_timeline.py -k "provenance"`
    - `pytest -q tests/test_runbook.py -k "provenance"`
    - `make test`

- [ ] ITK-021 (P1): Add deterministic redaction controls for diagnostics and evidence surfaces
  - Why (impact): dropped-line diagnostics and richer evidence snippets are useful, but risky to share raw. A built-in safe-sharing mode raises real-world usability without weakening parse-quality analysis.
  - DoD:
    - Add an opt-in redaction mode for dropped-line diagnostics plus timeline/runbook evidence/example surfaces.
    - Redaction is deterministic and uses stable placeholders for at least emails, IP addresses, UUID/correlation-style identifiers, and long token-like secrets.
    - Redaction happens after parse-quality evaluation so strict parse behavior, counters, and error classification do not change.
    - README documents placeholder policy, ordering guarantees, and the limits of built-in redaction.
    - Regression tests prove identical input yields identical redacted output across parse/timeline/runbook paths.
  - Verification:
    - `pytest -q tests/test_cli.py -k "redact or diagnostics"`
    - `pytest -q tests/test_timeline.py -k "redact or evidence"`
    - `pytest -q tests/test_runbook.py -k "redact or evidence"`
    - `make test`

- [ ] ITK-022 (P2): Surface per-source evidence concentration across summary/timeline/runbook
  - Why (impact): once provenance exists, operators should be able to see which file/stdin source dominates the incident slice instead of inferring it manually from raw logs.
  - DoD:
    - Add deterministic per-source evidence counts to the summary output and concise source callouts to timeline/runbook evidence sections.
    - Use the same stable source labels as parse output, including `-` for stdin.
    - Ordering is deterministic: `count DESC`, then earliest evidence timestamp, then source label text.
    - Preserve existing filter semantics and overall event ordering.
    - Update README and tests to document the new source-focused triage surface.
  - Verification:
    - `pytest -q tests/test_cli.py -k "summary and source"`
    - `pytest -q tests/test_timeline.py -k "source"`
    - `pytest -q tests/test_runbook.py -k "source"`
    - `make test`

- [ ] ITK-023 (P2): Make equal-timestamp determinism explicit across parse, timeline, runbook, and evidence helpers
  - Why (impact): deterministic merge order is part of the product promise, but some downstream helper paths still rely on implicit stable-sort behavior rather than an explicit tested contract.
  - DoD:
    - Lock same-timestamp ordering across multi-file and file+stdin inputs for parse output, timeline rows, runbook examples, and signature/component evidence derivation.
    - Ensure repeated filters do not disturb the original deterministic tie-break order.
    - Document the end-to-end tie-break contract in README.
    - Add regression tests for same-timestamp cross-source incidents.
  - Verification:
    - `pytest -q tests/test_cli.py -k "stdin or tied or order"`
    - `pytest -q tests/test_timeline.py -k "order or deterministic"`
    - `pytest -q tests/test_runbook.py -k "order or deterministic"`
    - `make test`

- [ ] ITK-024 (P2): Add golden/contract coverage for the summary JSON automation surface
  - Why (impact): `triage summary` is the main machine-readable handoff surface. Provenance/source/redaction work will make accidental contract drift more likely unless the JSON output shape is locked more tightly.
  - DoD:
    - Add dedicated contract/golden tests for summary schema version, empty/filter-miss states, `parse_summary` passthrough, `top_components`, `top_error_signatures`, and correlation coverage ordering.
    - Cover single-input and multi-input cases so future additive changes are deliberate and reviewable.
    - Update README examples if the locked contract changes.
  - Verification:
    - `pytest -q tests/test_cli.py -k "summary and (schema or contract or golden)"`
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
