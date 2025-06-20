# Python Template Makefile
# Common development tasks

.PHONY: help install test lint format type-check clean run dev setup-dev all-checks

# Default target
help:
	@echo "Python Template - Available commands:"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  install     Install dependencies using UV"
	@echo "  setup-dev   Setup development environment"
	@echo ""
	@echo "Development:"
	@echo "  run         Run the application"
	@echo "  dev         Run in development mode"
	@echo "  test        Run tests"
	@echo "  test-cov    Run tests with coverage"
	@echo ""
	@echo "Code Quality:"
	@echo "  format      Format code with black and isort"
	@echo "  lint        Lint code with flake8"
	@echo "  type-check  Type check with mypy"
	@echo "  all-checks  Run all quality checks"
	@echo ""
	@echo "Cleanup:"
	@echo "  clean       Clean build artifacts and cache"
	@echo "  clean-all   Clean everything including virtual env"

# Installation and Setup
install:
	uv sync

setup-dev:
	uv sync --dev
	uv run pre-commit install

# Running the application
run:
	uv run python-template run

dev:
	uv run python-template run --env development --log-level DEBUG

# Testing
test:
	uv run pytest

test-cov:
	uv run pytest --cov=src/python_template --cov-report=html --cov-report=term

test-verbose:
	uv run pytest -v

# Code Quality
format:
	uv run black src/ tests/
	uv run isort src/ tests/

lint:
	uv run flake8 src/ tests/

type-check:
	uv run mypy src/

all-checks: format lint type-check test
	@echo "All quality checks completed!"

# Build and Distribution
build:
	uv build

# Cleanup
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name "build" -exec rm -rf {} +
	find . -type d -name "dist" -exec rm -rf {} +
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	rm -rf .coverage

clean-all: clean
	rm -rf .venv/

# Development utilities
logs:
	@echo "Recent log entries:"
	@tail -n 20 logs/app.log 2>/dev/null || echo "No log file found"

info:
	uv run python-template info

config:
	uv run python-template config

# Docker (if needed)
docker-build:
	docker build -t python-template .

docker-run:
	docker run --rm -it python-template

# Environment management
env-dev:
	@echo "Setting up development environment variables..."
	cp .env.example .env
	@echo "Please edit .env file with your configuration"

# Pre-commit hooks
pre-commit:
	uv run pre-commit run --all-files

# Install/update pre-commit hooks
update-hooks:
	uv run pre-commit autoupdate 