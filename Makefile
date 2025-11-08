.PHONY: help install dev test lint format run docker-up docker-down migrate

help:
	@echo "Available commands:"
	@echo "  install      Install production dependencies"
	@echo "  dev          Install development dependencies"
	@echo "  test         Run tests with coverage"
	@echo "  lint         Run linting checks"
	@echo "  format       Format code"
	@echo "  run          Run the application"
	@echo "  docker-up    Start Docker services"
	@echo "  docker-down  Stop Docker services"
	@echo "  migrate      Run database migrations"

install:
	pip install --upgrade pip
	pip install -r requirements.txt

dev:
	pip install --upgrade pip
	pip install -r requirements-dev.txt
	pre-commit install
	cp .env.example .env

test:
	pytest tests/ -v --cov=app --cov-report=html --cov-report=term

lint:
	black --check app tests
	isort --check-only app tests
	flake8 app tests
	mypy app
	bandit -r app
	safety check

format:
	black app tests
	isort app tests

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port ${PORT:-8080}

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

migrate:
	alembic upgrade head

celery:
	celery -A app.celery_app worker --loglevel=info

flower:
	celery -A app.celery_app flower
