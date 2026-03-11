# ai_todo.md (deterministic)

Rule: work ONLY on the **first unchecked top-level** item.

Priority refresh basis: `docs/status.md` + `docs/critical_todo.md` + live repo verification (2026-03-11 21:20 UTC):
- `git status --short --branch` ✅ clean `main...origin/main`
- `make test` ✅ (`118 passed`)
- `docs/status.md` ✅ exists and confirms ITK-025 is complete while explicitly queuing ITK-026 next
- `docs/critical_todo.md` ✅ exists and has no open critical items
- Current repo facts from this maintenance pass:
  - dedicated golden fixtures exist for `parse`, `summary`, `timeline`, and `runbook`
  - focused helper coverage exists for `triage_toolkit/evidence.py` in `tests/test_evidence.py`
  - parser coverage already exists in `tests/test_parser.py`, but some parser helper/builder behaviors are still validated only indirectly
  - there is still no focused `tests/test_cli_helpers.py`
  - there is still no focused `tests/test_redaction.py`
  - there is still no dedicated cross-surface parity suite that proves `summary`, `timeline`, and `runbook` stay aligned on the same filtered incident slice
  - current redaction coverage is strong on targeted assertions, but not yet locked with full redacted golden outputs
- Highest-leverage remaining gaps after the latest verification:
  - shared CLI ingestion/filter/strict-gate plumbing is still protected mostly through broader command tests
  - regex-heavy redaction behavior is exercised end-to-end, but not yet locked with a focused helper suite
  - cross-command output parity still depends on separate assertions instead of one shared fixture-driven contract
  - full redacted output surfaces are not yet frozen with golden fixtures

## Open priorities (highest engineering impact first)

- [x] ITK-025 (P1): Add direct unit coverage for shared evidence and ranking helpers
  - Why (impact): `triage_toolkit/evidence.py` now drives summary, timeline, and runbook behavior. A small helper regression can therefore break several surfaces at once while only failing through higher-level tests, which makes root cause slower to pinpoint.
  - DoD:
    - Add `tests/test_evidence.py` covering `is_error`, `order_events`, signature normalization/ranking, source-evidence ranking, component ranking, and representative correlation-ID selection.
    - Include tied-timestamp cases that prove helper-level ordering stays aligned with the documented CLI determinism contract.
    - Cover redaction-aware signature rendering without duplicating full markdown/JSON golden payloads.
  - Verification:
    - `pytest -q tests/test_evidence.py`
    - `pytest -q tests/test_cli.py -k "summary or redact or deterministic"`
    - `make test`

- [x] ITK-026 (P1): Add direct unit coverage for shared CLI ingestion, strict-gate, filter, and write-path helpers
  - Why (impact): `triage_toolkit/cli.py` owns parse-summary aggregation, diagnostics-budget carry-forward, strict parse gating, reusable event-slice filters, and the shared stdout/file write path for every command. Those rules are critical, but most failures still surface first through broader command tests.
  - DoD:
    - Add `tests/test_cli_helpers.py` covering `_merge_parse_summaries`, `_apply_event_filters`, `_strict_parse_error`, `_read_events_for_parse`, and `_write_output`.
    - Lock repeated-flag OR semantics, cross-filter AND semantics, aggregate drop-ratio rounding, bounded diagnostics carry-forward, duplicate-stdin rejection, and parent-directory creation for file outputs.
    - Keep helper expectations aligned with the public CLI/README contract rather than inventing a separate private contract.
  - Verification:
    - `pytest -q tests/test_cli_helpers.py`
    - `pytest -q tests/test_cli.py -k "strict or filter or diagnostics or per_source or write"`
    - `make test`

- [ ] ITK-027 (P1): Add direct unit coverage for shared redaction helpers and placeholder stability
  - Why (impact): `triage_toolkit/redaction.py` feeds parse diagnostics and the redacted timeline/runbook surfaces. Because the implementation is regex-heavy and order-sensitive, a subtle change can silently alter what operators redact or leak without tripping a narrowly targeted test.
  - DoD:
    - Add `tests/test_redaction.py` covering deterministic placeholder reuse for emails, IPv4/IPv6 values, UUIDs, correlation/request/trace IDs, JWTs, and long token-like secrets.
    - Lock the current false-positive boundaries so all-digit and all-alpha long tokens are not redacted as secrets, while mixed long tokens still are.
    - Cover replacement ordering so keyed IDs preserve their key names (for example `cid=` / `trace_id=`) and values are not double-redacted.
  - Verification:
    - `pytest -q tests/test_redaction.py`
    - `pytest -q tests/test_cli.py -k "redact or diagnostics"`
    - `make test`

- [ ] ITK-028 (P2): Add a fixture-driven parity suite proving `summary`, `timeline`, and `runbook` stay aligned on the same filtered incident slice
  - Why (impact): the repo now relies on shared evidence/filtering helpers across multiple output surfaces. Individual command tests can all pass while counts, signatures, or source-ranking drift subtly across surfaces. One parity suite would catch that class of regression faster.
  - DoD:
    - Add a dedicated parity test module (for example `tests/test_output_parity.py`) that runs the same multi-input fixture through `summary`, `timeline`, and `runbook`.
    - Assert the same filtered slice yields matching evidence counts, top signature ordering, source concentration ordering, and first/last observed timestamps across all three outputs.
    - Include at least one file+stdin case and one empty-slice case so parity holds for the two trickiest shared paths.
  - Verification:
    - `pytest -q tests/test_output_parity.py`
    - `pytest -q tests/test_cli.py -k "summary or timeline or runbook"`
    - `make test`

- [ ] ITK-029 (P2): Tighten parser helper coverage for provenance extraction, diagnostics builders, and source-order propagation
  - Why (impact): `triage_toolkit/parser.py` is the ingestion root for every command. It already has decent end-to-end coverage, but some small helper/builder behaviors still fail only indirectly even though they control provenance metadata, drop diagnostics, and source-order propagation used later by the shared ordering helpers.
  - DoD:
    - Expand parser-focused tests to cover `_source_timestamp_provenance`, `_build_parse_summary`, `_build_dropped_line_diagnostic`, and `source_order` propagation through `parse_lines_with_summary`.
    - Lock mixed JSON/text drop-reason boundaries so invalid JSON, missing timestamps, invalid timestamps, blank lines, and unrecognized text stay classified as documented.
    - Keep expectations on public event/summary fields and deterministic ordering, not on incidental internal iteration details.
  - Verification:
    - `pytest -q tests/test_parser.py -k "provenance or diagnostics or source_order or dropped_reason"`
    - `pytest -q tests/test_cli.py -k "parse and provenance"`
    - `make test`

- [ ] ITK-030 (P3): Add full redacted golden fixtures for parse diagnostics, timeline, and runbook outputs
  - Why (impact): current redaction tests prove placeholder presence and reuse, but they do not freeze the full rendered output shape. Golden fixtures would catch drift in section ordering, placeholder placement, and markdown/JSON rendering across the complete redacted surfaces.
  - DoD:
    - Add golden fixtures for `triage parse --redact --diagnostics-limit N`, `triage timeline --redact`, and `triage runbook --redact`.
    - Assert stable placeholder reuse across full outputs rather than only a few targeted substrings.
    - Reuse one compact sensitive fixture so the golden outputs stay readable and cheap to review.
  - Verification:
    - `pytest -q tests/test_cli.py -k "redact"`
    - `pytest -q tests/test_timeline.py -k "redact"`
    - `pytest -q tests/test_runbook.py -k "redact"`
    - `make test`

---

Recently completed (kept brief so the live queue stays short):

- [x] ITK-024 (P1): Add dedicated golden/contract coverage for the summary JSON automation surface
- [x] ITK-023 (P1): Make equal-timestamp determinism explicit across shared ordering helpers
- [x] ITK-022 (P1): Finish per-source evidence concentration in timeline and runbook output
- [x] ITK-021 (P1): Add deterministic redaction controls for diagnostics and evidence surfaces
- [x] ITK-020 (P1): Preserve source provenance for successful parsed events and rendered evidence
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
