.PHONY: help install install-dev lock clean clean-venv test test-cov lint lint-fix format type-check build publish

ACTIVATE := . .venv/bin/activate

help:
	@echo "uncertainAPI - Development Commands"
	@echo ""
	@echo "  make install       Install minimal core"
	@echo "  make install-dev   Install development dependencies"
	@echo "  make lock          Regenerate poetry.lock"
	@echo "  make test          Run tests"
	@echo "  make test-cov      Run tests with coverage"
	@echo "  make lint          Run Ruff"
	@echo "  make lint-fix      Run Ruff with fixes"
	@echo "  make format        Format with Black"
	@echo "  make type-check    Run mypy"
	@echo "  make build         Build package"
	@echo "  make publish       Publish package"
	@echo "  make clean         Remove build/cache artifacts"

install:
	poetry config virtualenvs.in-project true
	poetry install --only main

install-dev:
	poetry config virtualenvs.in-project true
	poetry install --extras dev

lock:
	poetry lock

test:
	poetry run pytest

test-cov:
	poetry run pytest --cov=uncertainAPI --cov-report=term-missing --cov-report=html

lint:
	poetry run ruff check uncertainAPI/

lint-fix:
	poetry run ruff check --fix uncertainAPI/

format:
	poetry run black uncertainAPI/

type-check:
	poetry run mypy uncertainAPI/

build:
	poetry build

publish:
	poetry publish

clean:
	@rm -rf build dist *.egg-info htmlcov .coverage .pytest_cache .mypy_cache .ruff_cache .tox
	@find . -name '__pycache__' -type d -prune -exec rm -rf {} + 2>/dev/null || true
	@find . -name '*.pyc' -delete 2>/dev/null || true

clean-venv:
	@rm -rf .venv
