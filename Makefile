PYTHON ?= python3
VENV ?= .venv
VENV_PY := $(VENV)/bin/python

setup:
	$(PYTHON) -m venv $(VENV)
	$(VENV_PY) -m pip install -U pip
	$(VENV_PY) -m pip install -e .[dev]
	@echo "Activated venv (Linux/macOS): source $(VENV)/bin/activate"
	@echo "Windows PowerShell: . $(VENV)\\Scripts\\Activate.ps1"

lint:
	$(VENV_PY) -m ruff check .

test:
	$(VENV_PY) -m pytest

run:
	$(VENV_PY) -m triage_toolkit.cli timeline samples/app.log --out timeline.md
