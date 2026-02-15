# ai_todo.md (deterministic)

Rule: work ONLY on the **first unchecked top-level** item.

- [x] ITK-001: Add installable packaging + `triage` console script
  - DoD:
    - Add `pyproject.toml` so `python -m pip install -e .` works
    - `triage --help` works (entrypoint wired to `triage_toolkit.cli:main`)
    - `make setup`, `make lint`, `make test` work on Linux (default `python3`)
    - Update `README.md` with a Linux/macOS quickstart (keep PowerShell section too)

- [x] ITK-002: Add CI (GitHub Actions) for lint + tests
  - DoD:
    - Workflow runs `ruff` + `pytest` on push/PR
    - Uses at least Python 3.11
    - README has a build status badge

- [x] ITK-003: CLI UX improvements (small, safe)
  - DoD (examples):
    - Allow `--out -` to write to stdout
    - Better error messages for unreadable/missing files
    - Add `--version` flag (reads from package version)
