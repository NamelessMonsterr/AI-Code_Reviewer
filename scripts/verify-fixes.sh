#!/bin/bash
set -e

echo "🔍 Verifying all fixes..."

echo "1. Testing OpenAI API migration..."
pytest tests/test_doc_generator.py tests/test_chat_interface.py -v

echo "2. Testing Phase 4 features..."
pytest tests/test_phase4_comprehensive.py -v

echo "3. Testing Phase 5 features..."
pytest tests/test_phase5_comprehensive.py -v

echo "4. Checking code coverage..."
pytest tests/ --cov=src --cov-report=term --cov-fail-under=85

echo "5. Running linters..."
flake8 src/ --max-line-length=120
pylint src/ --max-line-length=120

echo "6. Security scan..."
bandit -r src/ -ll

echo "✅ All verifications passed!"
