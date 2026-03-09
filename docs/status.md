# status.md

## Current state
- Repo: incident-triage-toolkit (Python CLI)
- Goal: parse heterogeneous logs, generate a timeline, and draft an RCA/runbook skeleton.

## Work mode
- Deterministic TODO: `docs/ai_todo.md` (first unchecked top-level only)
- If `docs/user_todo.md` has any unchecked items → STOP.

## Latest updates
- ITK-018 completed (deterministic stdin ingestion across CLI commands):
  - `triage_toolkit/cli.py`: `parse`, `summary`, `timeline`, and `runbook` now accept `-` as a UTF-8 stdin source.
  - Mixing is explicit and deterministic: stdin may appear at most once, stdin is labeled as `-` in parse summaries/diagnostics, and merged event ordering still follows UTC timestamp → CLI input order → line order within source.
  - Strict parse gates still evaluate the full raw ingested input when stdin participates, so pipe-based workflows cannot bypass parse-quality checks.
  - `tests/test_cli.py`: added stdin-only coverage for all four commands, mixed file+stdin ordering coverage, duplicate-stdin rejection, and strict-parse stdin regression coverage.
  - `tests/test_parser.py`: added parser-level coverage for the stable stdin source label in dropped-line diagnostics.
  - `README.md`: documented stdin examples, mixing rules, and a PowerShell caveat.
- Why:
  - Operators can now use shell-native incident workflows (`kubectl logs`, `journalctl`, pasted snippets, prefiltered pipelines) without temp files.
- Risks / follow-ups:
  - Current stdin handling reads the provided stdin payload once per command invocation, which is correct for the CLI contract but should stay documented if streaming semantics ever expand.
  - Next highest-impact product gap is ITK-017 (make runbook output more evidence-driven).
- Verification run:
  - `.venv/bin/python -m pytest -q tests/test_cli.py -k "stdin or standard_input"` ✅
  - `.venv/bin/python -m pytest -q tests/test_parser.py -k "stream or stdin"` ✅
  - `make test` ✅

## Next
- Start ITK-017 by making runbook output more evidence-driven while preserving deterministic ordering and markdown contract stability.
