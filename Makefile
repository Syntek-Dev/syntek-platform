# Makefile for Django/PostgreSQL/GraphQL project
.PHONY: help install dev test clean lint format migrate shell superuser docker-up docker-down

# Default target
.DEFAULT_GOAL := help

# Variables
PYTHON := python3
PIP := $(PYTHON) -m pip
DJANGO := $(PYTHON) manage.py
DOCKER_COMPOSE := docker-compose

# Colors for output
COLOR_RESET := \033[0m
COLOR_BOLD := \033[1m
COLOR_GREEN := \033[32m
COLOR_YELLOW := \033[33m
COLOR_BLUE := \033[34m

help: ## Show this help message
	@echo "$(COLOR_BOLD)Available commands:$(COLOR_RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(COLOR_GREEN)%-20s$(COLOR_RESET) %s\n", $$1, $$2}'

# Installation and Setup
install: ## Install all dependencies
	@echo "$(COLOR_BLUE)Installing dependencies...$(COLOR_RESET)"
	$(PIP) install --upgrade pip
	$(PIP) install -e ".[dev]"
	@echo "$(COLOR_GREEN)Dependencies installed successfully!$(COLOR_RESET)"

install-prod: ## Install production dependencies only
	@echo "$(COLOR_BLUE)Installing production dependencies...$(COLOR_RESET)"
	$(PIP) install --upgrade pip
	$(PIP) install -e .
	@echo "$(COLOR_GREEN)Production dependencies installed!$(COLOR_RESET)"

install-dev: ## Install development dependencies
	@echo "$(COLOR_BLUE)Installing development dependencies...$(COLOR_RESET)"
	$(PIP) install --upgrade pip
	$(PIP) install -e ".[dev]"
	pre-commit install
	@echo "$(COLOR_GREEN)Development dependencies installed!$(COLOR_RESET)"

# Development
dev: ## Run development server
	@echo "$(COLOR_BLUE)Starting development server...$(COLOR_RESET)"
	$(DJANGO) runserver 0.0.0.0:8000

migrate: ## Run database migrations
	@echo "$(COLOR_BLUE)Running migrations...$(COLOR_RESET)"
	$(DJANGO) migrate
	@echo "$(COLOR_GREEN)Migrations completed!$(COLOR_RESET)"

makemigrations: ## Create new migrations
	@echo "$(COLOR_BLUE)Creating migrations...$(COLOR_RESET)"
	$(DJANGO) makemigrations
	@echo "$(COLOR_GREEN)Migrations created!$(COLOR_RESET)"

shell: ## Start Django shell
	@echo "$(COLOR_BLUE)Starting Django shell...$(COLOR_RESET)"
	$(DJANGO) shell_plus

superuser: ## Create a superuser
	@echo "$(COLOR_BLUE)Creating superuser...$(COLOR_RESET)"
	$(DJANGO) createsuperuser

# Testing
test: ## Run tests with pytest
	@echo "$(COLOR_BLUE)Running tests...$(COLOR_RESET)"
	pytest
	@echo "$(COLOR_GREEN)Tests completed!$(COLOR_RESET)"

test-fast: ## Run tests without coverage
	@echo "$(COLOR_BLUE)Running fast tests...$(COLOR_RESET)"
	pytest --no-cov
	@echo "$(COLOR_GREEN)Fast tests completed!$(COLOR_RESET)"

test-unit: ## Run only unit tests
	@echo "$(COLOR_BLUE)Running unit tests...$(COLOR_RESET)"
	pytest -m unit
	@echo "$(COLOR_GREEN)Unit tests completed!$(COLOR_RESET)"

test-integration: ## Run only integration tests
	@echo "$(COLOR_BLUE)Running integration tests...$(COLOR_RESET)"
	pytest -m integration
	@echo "$(COLOR_GREEN)Integration tests completed!$(COLOR_RESET)"

test-cov: ## Run tests with coverage report
	@echo "$(COLOR_BLUE)Running tests with coverage...$(COLOR_RESET)"
	pytest --cov --cov-report=html --cov-report=term
	@echo "$(COLOR_GREEN)Coverage report generated in htmlcov/$(COLOR_RESET)"

# Code Quality
lint: ## Run all linters
	@echo "$(COLOR_BLUE)Running linters...$(COLOR_RESET)"
	ruff check .
	ruff format --check .
	mypy .
	@echo "$(COLOR_GREEN)Linting completed!$(COLOR_RESET)"

lint-fix: ## Run linters and auto-fix issues
	@echo "$(COLOR_BLUE)Running linters with auto-fix...$(COLOR_RESET)"
	ruff check --fix .
	ruff format .
	@echo "$(COLOR_GREEN)Auto-fix completed!$(COLOR_RESET)"

format: ## Format code with ruff
	@echo "$(COLOR_BLUE)Formatting code...$(COLOR_RESET)"
	ruff format .
	ruff check --fix .
	@echo "$(COLOR_GREEN)Code formatted!$(COLOR_RESET)"

check: ## Run pre-commit checks on all files
	@echo "$(COLOR_BLUE)Running pre-commit checks...$(COLOR_RESET)"
	pre-commit run --all-files
	@echo "$(COLOR_GREEN)Pre-commit checks completed!$(COLOR_RESET)"

# Static Files
collectstatic: ## Collect static files
	@echo "$(COLOR_BLUE)Collecting static files...$(COLOR_RESET)"
	$(DJANGO) collectstatic --noinput
	@echo "$(COLOR_GREEN)Static files collected!$(COLOR_RESET)"

# Database
db-reset: ## Reset database (WARNING: destroys all data)
	@echo "$(COLOR_YELLOW)WARNING: This will destroy all database data!$(COLOR_RESET)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		echo "$(COLOR_BLUE)Resetting database...$(COLOR_RESET)"; \
		$(DJANGO) flush --noinput; \
		$(DJANGO) migrate; \
		echo "$(COLOR_GREEN)Database reset completed!$(COLOR_RESET)"; \
	fi

db-backup: ## Backup database
	@echo "$(COLOR_BLUE)Backing up database...$(COLOR_RESET)"
	$(DJANGO) dumpdata --natural-foreign --natural-primary --exclude contenttypes --exclude auth.Permission > backup.json
	@echo "$(COLOR_GREEN)Database backed up to backup.json$(COLOR_RESET)"

db-restore: ## Restore database from backup
	@echo "$(COLOR_BLUE)Restoring database...$(COLOR_RESET)"
	$(DJANGO) loaddata backup.json
	@echo "$(COLOR_GREEN)Database restored!$(COLOR_RESET)"

# Docker
docker-build: ## Build Docker images
	@echo "$(COLOR_BLUE)Building Docker images...$(COLOR_RESET)"
	$(DOCKER_COMPOSE) build
	@echo "$(COLOR_GREEN)Docker images built!$(COLOR_RESET)"

docker-up: ## Start Docker containers
	@echo "$(COLOR_BLUE)Starting Docker containers...$(COLOR_RESET)"
	$(DOCKER_COMPOSE) up -d
	@echo "$(COLOR_GREEN)Docker containers started!$(COLOR_RESET)"

docker-down: ## Stop Docker containers
	@echo "$(COLOR_BLUE)Stopping Docker containers...$(COLOR_RESET)"
	$(DOCKER_COMPOSE) down
	@echo "$(COLOR_GREEN)Docker containers stopped!$(COLOR_RESET)"

docker-logs: ## Show Docker logs
	@echo "$(COLOR_BLUE)Showing Docker logs...$(COLOR_RESET)"
	$(DOCKER_COMPOSE) logs -f

docker-shell: ## Open shell in Docker container
	@echo "$(COLOR_BLUE)Opening shell in Docker container...$(COLOR_RESET)"
	$(DOCKER_COMPOSE) exec web bash

# GraphQL
graphql-schema: ## Generate GraphQL schema
	@echo "$(COLOR_BLUE)Generating GraphQL schema...$(COLOR_RESET)"
	$(DJANGO) graphql_schema --out schema.graphql
	@echo "$(COLOR_GREEN)GraphQL schema generated!$(COLOR_RESET)"

# Cleanup
clean: ## Clean up temporary files
	@echo "$(COLOR_BLUE)Cleaning up...$(COLOR_RESET)"
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
	find . -type d -name '*.egg-info' -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name '.pytest_cache' -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name '.mypy_cache' -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name 'htmlcov' -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '.coverage' -delete 2>/dev/null || true
	@echo "$(COLOR_GREEN)Cleanup completed!$(COLOR_RESET)"

clean-all: clean ## Clean everything including virtualenv
	@echo "$(COLOR_BLUE)Cleaning everything...$(COLOR_RESET)"
	rm -rf venv .venv
	@echo "$(COLOR_GREEN)Deep cleanup completed!$(COLOR_RESET)"

# Dependencies
deps-lock: ## Generate locked dependencies from pyproject.toml
	@echo "$(COLOR_BLUE)Locking dependencies...$(COLOR_RESET)"
	$(PIP) install pip-tools
	pip-compile pyproject.toml -o requirements.lock
	@echo "$(COLOR_GREEN)Dependencies locked to requirements.lock!$(COLOR_RESET)"

deps-upgrade: ## Upgrade all dependencies
	@echo "$(COLOR_BLUE)Upgrading dependencies...$(COLOR_RESET)"
	$(PIP) install --upgrade -e ".[dev]"
	@echo "$(COLOR_GREEN)Dependencies upgraded!$(COLOR_RESET)"

# CI/CD
ci-test: ## Run tests for CI/CD
	@echo "$(COLOR_BLUE)Running CI tests...$(COLOR_RESET)"
	pytest --verbose --cov --cov-report=xml --cov-report=term
	@echo "$(COLOR_GREEN)CI tests completed!$(COLOR_RESET)"

ci-lint: ## Run linting for CI/CD
	@echo "$(COLOR_BLUE)Running CI linting...$(COLOR_RESET)"
	ruff check . --output-format=github
	ruff format --check .
	@echo "$(COLOR_GREEN)CI linting completed!$(COLOR_RESET)"
