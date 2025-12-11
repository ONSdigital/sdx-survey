SHELL := bash
.ONESHELL:


PHONY: install
install: ## Install dependencies
	uv sync


.PHONY: test
test: install
	@echo "Running tests..."
	uv run pytest -v --cov-report term-missing --disable-warnings --cov=app tests/


.PHONY: lint
lint:
	@echo "Running Ruff linter..."
	uv run --only-group lint ruff check --fix


.PHONY: dev
dev:
	@echo "Starting development server..."
	uv run run.py


.PHONY: bump
bump:
	@echo "🔼 Bumping project version..."
	uv run --only-group version-check python .github/scripts/bump_version.py
	@echo "🔄 Generating new lock file..."
	uv lock
