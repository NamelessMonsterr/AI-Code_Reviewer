#!/bin/bash
set -e

echo "🧪 Running tests..."
echo ""

# Run pytest with coverage
pytest tests/ \
    --verbose \
    --cov=src \
    --cov-report=html \
    --cov-report=term \
    --cov-report=xml

echo ""
echo "📊 Coverage report generated: htmlcov/index.html"


# ============================================
# FILE: scripts/lint.sh
# ============================================
#!/bin/bash
set -e

echo "🔍 Running linters..."
echo ""

# Run flake8
echo "Running flake8..."
flake8 src/ --max-line-length=120 --exclude=__pycache__

# Run pylint
echo ""
echo "Running pylint..."
pylint src/ --max-line-length=120

# Run mypy
echo ""
echo "Running mypy..."
mypy src/ --ignore-missing-imports

# Run bandit
echo ""
echo "Running bandit (security)..."
bandit -r src/ -ll

echo ""
echo "✅ All linters passed!"
