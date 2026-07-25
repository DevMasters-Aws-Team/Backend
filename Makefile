.PHONY: install run test lint format docker-build docker-up docker-down

install:
	poetry install

run:
	poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

test:
	poetry run pytest tests/ -v --cov=src --cov-fail-under=80

lint:
	poetry run ruff check src/
	poetry run black --check src/
	poetry run mypy src/ --ignore-missing-imports

format:
	poetry run ruff check src/ --fix
	poetry run black src/

docker-build:
	docker build -t kiro-log-generator .

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down
