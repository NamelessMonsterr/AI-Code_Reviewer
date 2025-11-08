.PHONY: help install install-dev test lint format clean run

help:
	@echo "Available commands:"
	@echo "  install      Install production dependencies"
	@echo "  install-dev  Install development dependencies"
	@echo "  test         Run tests with coverage"
	@echo "  lint         Run linting checks"
	@echo "  format       Format code with black and isort"
	@echo "  clean        Clean cache files"
	@echo "  run          Run the application"

install:
	pip install --upgrade pip
	pip install -r requirements.txt

install-dev:
	pip install --upgrade pip
	pip install -r requirements-dev.txt
	pre-commit install

test:
	pytest -v --cov=app --cov-report=html --cov-report=term

lint:
	flake8 app tests
	pylint app
	mypy app
	bandit -r app
	safety check

format:
	black app tests
	isort app tests

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .coverage htmlcov .mypy_cache

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
