SHELL := /bin/zsh

.PHONY: help install run test \
	migrate current history heads downgrade \
	revision revision-empty

help:
	@echo "Available commands:"
	@echo "  make install                      Install backend dependencies"
	@echo "  make run                          Run FastAPI with reload"
	@echo "  make test                         Run tests"
	@echo "  make migrate                      Apply all migrations (upgrade head)"
	@echo "  make current                      Show current alembic revision"
	@echo "  make history                      Show migration history"
	@echo "  make heads                        Show alembic heads"
	@echo "  make downgrade                    Downgrade one migration step"
	@echo "  make revision m='message'         Create autogen migration"
	@echo "  make revision-empty m='message'   Create empty migration"

install:
	pip install -r requirements.txt

run:
	uvicorn app.main:app --reload --port 8000

test:
	pytest -q

migrate:
	alembic upgrade head

current:
	alembic current

history:
	alembic history

heads:
	alembic heads

downgrade:
	alembic downgrade -1

revision:
	@if [ -z "$(m)" ]; then \
		echo "Usage: make revision m='your_message'"; \
		exit 1; \
	fi
	alembic revision --autogenerate -m "$(m)"

revision-empty:
	@if [ -z "$(m)" ]; then \
		echo "Usage: make revision-empty m='your_message'"; \
		exit 1; \
	fi
	alembic revision -m "$(m)"
