.PHONY: help install dev run test lint typecheck clean venv

.DEFAULT_GOAL := help

# Variables
PYTHON := python3
VENV := venv
PIP := $(VENV)/bin/pip
PYTEST := $(VENV)/bin/pytest
RUFF := $(VENV)/bin/ruff
MYPY := $(VENV)/bin/mypy
ANIFLOW := $(VENV)/bin/aniflow

# Colors for output
COLOR_RESET := \033[0m
COLOR_BOLD := \033[1m
COLOR_GREEN := \033[92m
COLOR_YELLOW := \033[93m
COLOR_BLUE := \033[94m

help: ## Show this help message
	@echo "$(COLOR_BOLD)AniFlow - Anime Batch Downloader$(COLOR_RESET)"
	@echo "$(COLOR_BOLD)═════════════════════════════════════════$(COLOR_RESET)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(COLOR_GREEN)%-15s$(COLOR_RESET) %s\n", $$1, $$2}'

install: $(VENV) ## Install dependencies
	$(PIP) install -e .
	@echo "$(COLOR_GREEN)✓ Dependencies installed$(COLOR_RESET)"

dev: install ## Install with development dependencies
	$(PIP) install -e ".[dev]"
	@echo "$(COLOR_GREEN)✓ Development environment ready$(COLOR_RESET)"

venv: ## Create virtual environment
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip setuptools wheel
	@echo "$(COLOR_GREEN)✓ Virtual environment created$(COLOR_RESET)"

$(VENV): venv

run: install ## Run AniFlow interactive wizard
	$(ANIFLOW)

run-url: install ## Run AniFlow with URL (usage: make run-url URL="https://...")
	$(ANIFLOW) url "$(URL)"

run-search: install ## Run AniFlow with search (usage: make run-search QUERY="Attack on Titan")
	$(ANIFLOW) search "$(QUERY)"

test: dev ## Run all tests with coverage
	$(PYTEST)

test-unit: dev ## Run unit tests only
	$(PYTEST) tests/unit -v

test-integration: dev ## Run integration tests
	$(PYTEST) tests/integration -v -m integration

test-coverage: dev ## Show coverage report
	$(PYTEST) --cov-report=html
	@echo "$(COLOR_YELLOW)Coverage report generated in htmlcov/index.html$(COLOR_RESET)"

lint: dev ## Check code quality with ruff
	$(RUFF) check src/ tests/

lint-fix: dev ## Auto-fix ruff issues
	$(RUFF) check --fix src/ tests/

typecheck: dev ## Run mypy type checking
	$(MYPY) src/aniflow/

format: dev ## Format code with black and isort
	$(VENV)/bin/black src/ tests/
	$(VENV)/bin/isort src/ tests/

format-check: dev ## Check code formatting
	$(VENV)/bin/black --check src/ tests/
	$(VENV)/bin/isort --check-only src/ tests/

all-checks: lint typecheck format-check test ## Run all checks
	@echo "$(COLOR_GREEN)✓ All checks passed$(COLOR_RESET)"

clean: ## Remove build artifacts and caches
	rm -rf $(VENV) build/ dist/ *.egg-info htmlcov .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete
	@echo "$(COLOR_GREEN)✓ Cleaned up$(COLOR_RESET)"

requirements: install ## Generate requirements.txt
	$(PIP) freeze > requirements.txt
	@echo "$(COLOR_GREEN)✓ Requirements updated$(COLOR_RESET)"

.PHONY: docs
docs: ## Build documentation
	@echo "$(COLOR_YELLOW)Documentation setup coming soon$(COLOR_RESET)"
