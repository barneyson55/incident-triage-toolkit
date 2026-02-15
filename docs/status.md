# status.md

## Current state
- Repo: incident-triage-toolkit (Python CLI)
- Goal: parse heterogeneous logs, generate a timeline, and draft an RCA/runbook skeleton.

## Work mode
- Deterministic TODO: `docs/ai_todo.md` (first unchecked top-level only)
- If `docs/user_todo.md` has any unchecked items → STOP.

## Latest updates
- Completed ITK-003 (CLI UX improvements):
  - Updated `triage_toolkit/cli.py` to:
    - Support `--out -` (stdout) for `parse`, `timeline`, and `runbook`
    - Add a global `--version` flag that reads package metadata
    - Return clearer file I/O errors for missing, unreadable, directory, invalid UTF-8, and write-failure paths
  - Added `tests/test_cli.py` to cover:
    - `parse --out -` stdout behavior
    - Missing-file error messaging
    - `--version` output
- Why:
  - Improves CLI ergonomics for piping/automation and reduces ambiguity during operator triage.
- Risks / follow-ups:
  - `--version` falls back to `triage_toolkit.__version__` when package metadata is unavailable.
- Local verification executed:
  - `make lint` ✅
  - `make test` ✅ (7 passed)

## Next
- No open top-level items in `docs/ai_todo.md`.
