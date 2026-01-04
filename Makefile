PYTHON?=python

setup:
	$(PYTHON) -m venv .venv
	@echo "Activate with: .venv\\Scripts\\Activate.ps1 (PowerShell) or source .venv/Scripts/activate (Git Bash)"
	$(PYTHON) -m pip install -r requirements.txt -r requirements-dev.txt

lint:
	$(PYTHON) -m ruff check .

test:
	$(PYTHON) -m pytest

run:
	$(PYTHON) -m triage_toolkit.cli timeline samples/app.log --out timeline.md
