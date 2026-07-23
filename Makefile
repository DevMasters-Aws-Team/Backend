.PHONY: install dev test lint lint-fix docker-build docker-run clean

install:
	poetry install

dev:
	poetry run uvicorn kiro_agent.main:app --host 0.0.0.0 --port 8080 --reload

test:
	poetry run pytest tests/ -v

test-cov:
	poetry run pytest tests/ --cov=kiro_agent --cov-report=html

lint:
	poetry run ruff check kiro_agent/
	poetry run black --check kiro_agent/

lint-fix:
	poetry run ruff check kiro_agent/ --fix
	poetry run black kiro_agent/

docker-build:
	docker build -t kiro-backend:latest .

docker-run:
	docker run -p 8080:8080 --env-file .env kiro-backend:latest

clean:
	rm -rf .pytest_cache .coverage htmlcov dist build *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
