#!/bin/bash
# Run all tests with coverage

echo "🧪 Running tests..."

# Run tests with coverage
pytest tests/ \
    -v \
    --cov=src \
    --cov-report=html \
    --cov-report=term \
    --cov-report=xml \
    --tb=short \
    --strict-markers

# Check exit code
if [ $? -eq 0 ]; then
    echo "✅ All tests passed!"
else
    echo "❌ Some tests failed!"
    exit 1
fi

# Display coverage summary
echo ""
echo "📊 Coverage Report:"
coverage report --show-missing

echo ""
echo "📁 HTML coverage report: htmlcov/index.html"
