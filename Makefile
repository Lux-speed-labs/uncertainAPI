.PHONY: help install migrate test run clean docker-build docker-up docker-down

# Variables
PYTHON = python
PIP = pip
MANAGE = $(PYTHON) manage.py

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install dependencies
	$(PIP) install -r requirements.txt
	playwright install chromium

migrate: ## Run database migrations
	$(MANAGE) makemigrations
	$(MANAGE) migrate

test: ## Run tests
	$(MANAGE) test
	pytest

run: ## Run development server
	$(MANAGE) runserver

celery: ## Run Celery worker
	celery -A uncertainapi worker --loglevel=info

celery-beat: ## Run Celery beat scheduler
	celery -A uncertainapi beat --loglevel=info

shell: ## Open Django shell
	$(MANAGE) shell

superuser: ## Create superuser
	$(MANAGE) createsuperuser

clean: ## Clean Python cache files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +

lint: ## Run code linting
	flake8 .
	black --check .
	isort --check-only .

format: ## Format code
	black .
	isort .

docker-build: ## Build Docker images
	docker-compose build

docker-up: ## Start services with Docker Compose
	docker-compose up -d

docker-down: ## Stop Docker Compose services
	docker-compose down

docker-logs: ## View Docker logs
	docker-compose logs -f

setup-dev: install migrate superuser ## Setup development environment
	@echo "Development environment setup complete!"
	@echo "Run 'make run' to start the development server"