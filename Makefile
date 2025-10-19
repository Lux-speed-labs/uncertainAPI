.PHONY: help install install-dev lock lock-no-update clean test test-cov lint lint/fix format type-check build publish shell run check-venv

# Activate virtual environment
ACTIVATE := . .venv/bin/activate

# Install poetry if not available
define install_poetry
	if ! command -v poetry &> /dev/null; then \
		pip install --upgrade pip; \
		pip install 'poetry>=1.0.0'; \
	else \
		echo "Poetry is already installed."; \
	fi
endef

# Deactivate any active virtual environment
define deactivate_virtualenv
	if [ -n "$$VIRTUAL_ENV" ]; then \
		unset VIRTUAL_ENV; \
		unset PYTHONHOME; \
		unset -f pydoc >/dev/null 2>&1; \
		OLD_PATH="$$PATH"; \
		PATH=$$(echo -n "$$PATH" | awk -v RS=: -v ORS=: '/\/virtualenv\/bin$$/ {next} {print}'); \
		export PATH; \
		hash -r; \
		echo "Deactivated the virtual environment."; \
	fi
endef

# Check if virtual environment exists (used by most targets)
check-venv:
	@if [ ! -d ".venv" ]; then \
		echo "\033[0;31mError: Virtual environment not found!\033[0m"; \
		echo "Please run 'make install-dev' or 'make install' first to create it."; \
		exit 1; \
	fi

# Default target
help:
	@echo "uncertainAPI - Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install        Install package and create virtual environment"
	@echo "  make install-dev    Install with development dependencies"
	@echo "  make lock           Update poetry.lock with latest dependencies"
	@echo "  make lock-no-update Update poetry.lock without updating dependencies"
	@echo ""
	@echo "Development:"
	@echo "  make shell          Activate virtual environment shell"
	@echo "  make run            Run the main application"
	@echo "  make test           Run tests"
	@echo "  make test-cov       Run tests with coverage report"
	@echo "  make lint           Run linter checks (ruff)"
	@echo "  make lint/fix       Run linter and auto-fix issues"
	@echo "  make format         Format code with black"
	@echo "  make type-check     Run type checker (mypy)"
	@echo ""
	@echo "Build & Publish:"
	@echo "  make build          Build distribution packages"
	@echo "  make publish        Publish to PyPI"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean          Remove build artifacts and cache files"
	@echo "  make clean-venv     Remove virtual environment"

# Install package (creates venv in root directory)
install:
	$(call deactivate_virtualenv) && \
	$(call install_poetry) && \
	poetry config virtualenvs.in-project true && \
	poetry env remove --all 2>/dev/null || true && \
	poetry install --no-dev
	@echo "\033[0;32mVirtual environment created at .venv/\033[0m"

# Install with development dependencies (creates venv in root directory)
install-dev:
	$(call deactivate_virtualenv) && \
	$(call install_poetry) && \
	poetry config virtualenvs.in-project true && \
	poetry env remove --all 2>/dev/null || true && \
	poetry install
	@echo "\033[0;32mVirtual environment created at .venv/\033[0m"

# Update poetry.lock with latest dependencies
lock: check-venv
	@echo "Updating poetry.lock..."
	$(ACTIVATE) && poetry lock
	@echo "\033[0;32m✓ Lock file updated!\033[0m"

# Update poetry.lock without updating dependencies
lock-no-update: check-venv
	@echo "Updating poetry.lock (no update)..."
	$(ACTIVATE) && poetry lock --no-update
	@echo "\033[0;32m✓ Lock file updated!\033[0m"

# Activate shell in virtual environment
shell: check-venv
	@echo "Activating virtual environment..."
	@echo "Run 'deactivate' to exit the virtual environment."
	@$(ACTIVATE) && $$SHELL

# Run the main application
run: check-venv
	$(ACTIVATE) && python -m uncertainAPI.main

# Run tests
test: check-venv
	$(ACTIVATE) && pytest

# Run tests with coverage
test-cov: check-venv
	$(ACTIVATE) && pytest --cov=uncertainAPI --cov-report=term-missing --cov-report=html

# Run linter (check only)
lint: check-venv
	@echo "Running linter checks..."
	@$(ACTIVATE) && ruff check uncertainAPI/ && echo "\033[0;32m✓ Linting passed!\033[0m" || echo "\033[0;31m✗ Linting failed!\033[0m"

# Run linter with auto-fix
lint/fix: check-venv
	@echo "Running linter with auto-fix..."
	@$(ACTIVATE) && ruff check --fix uncertainAPI/ && echo "\033[0;32m✓ Linting complete!\033[0m"

# Format code
format: check-venv
	$(ACTIVATE) && black uncertainAPI/ && ruff check --fix uncertainAPI/

# Run type checker
type-check: check-venv
	$(ACTIVATE) && mypy uncertainAPI/

# Build distribution packages
build: check-venv
	$(ACTIVATE) && poetry build

# Publish to PyPI
publish: check-venv
	$(ACTIVATE) && poetry publish

# Clean build artifacts and cache
clean:
	@echo "Cleaning build artifacts and cache..."
	@find . -name '*.pyc' -exec rm -rf {} \; 2>/dev/null || true
	@find . -name '__pycache__' -type d -exec rm -rf {} \; 2>/dev/null || true
	@find . -name 'Thumbs.db' -exec rm -rf {} \; 2>/dev/null || true
	@find . -name '*~' -exec rm -rf {} \; 2>/dev/null || true
	@rm -rf .cache
	@rm -rf build
	@rm -rf dist
	@rm -rf *.egg-info
	@rm -rf htmlcov
	@rm -rf .coverage
	@rm -rf .pytest_cache
	@rm -rf .mypy_cache
	@rm -rf .ruff_cache
	@rm -rf .tox
	@rm -rf docs/_build
	@echo "\033[0;32mClean complete!\033[0m"

# Remove virtual environment
clean-venv:
	@echo "Removing virtual environment..."
	@rm -rf .venv
	@echo "\033[0;32mVirtual environment removed!\033[0m"
	@echo "Run 'make install-dev' to recreate it."
