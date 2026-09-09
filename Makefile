PYTHON ?= python3
VENV_PYTHON := .venv/bin/python
ifeq ($(OS),Windows_NT)
PYTHON := python
VENV_PYTHON := .venv/Scripts/python.exe
endif

.PHONY: setup test eval demo deploy check format lint typecheck security api web up down synth container-smoke aws-smoke live-eval financial-pipeline financial-smoke
setup:
	$(PYTHON) scripts/tasks.py setup
test eval demo deploy check format lint typecheck security api web up down synth container-smoke aws-smoke live-eval financial-pipeline financial-smoke:
	$(VENV_PYTHON) scripts/tasks.py $@
