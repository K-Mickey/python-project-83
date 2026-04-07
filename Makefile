install:
	uv sync

lint:
	uv run ruff check page_analyzer --fix

dev:
	uv run flask --debug --app page_analyzer:app run

test:
	uv run pytest

test-coverage:
	uv run pytest --cov=page_analyzer --cov-report xml

check: test lint

.PHONY: install lint dev test test-coverage check