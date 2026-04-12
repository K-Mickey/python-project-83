ifneq (,$(wildcard .env))
    include .env
    export
endif

install:
	uv sync --frozen && uv cache prune --ci

build:
	./build.sh

lint:
	uv run ruff check page_analyzer --fix

dev:
	uv run flask --debug --app page_analyzer:app run

PORT ?= 8000
start:
	uv run gunicorn -w 5 -b 0.0.0.0:${PORT} page_analyzer:app

migrate:
	@echo "Migrating database..."
	psql -a -d "${DATABASE_URL}" -f database.sql
	@echo "Database migrated"

test:
	DATABASE_URL=${TEST_BASE_DB_URL} uv run pytest

test-coverage:
	DATABASE_URL=${TEST_BASE_DB_URL} uv run pytest --cov=page_analyzer --cov-report xml

check: test lint

.PHONY: install build lint dev start test test-coverage check