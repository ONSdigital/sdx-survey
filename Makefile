SHELL := bash
.ONESHELL:


PHONY: install
install: ## Install dependencies
	uv sync


.PHONY: test
test:
	uv run pytest -v --cov-report term-missing --disable-warnings --cov=app tests/


.PHONY: lint
lint:
	uv run flake8 . --count --statistics
