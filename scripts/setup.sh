#!/bin/bash

echo "🚀 Setting up AI Code Reviewer..."

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🌍 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Clean requirements.txt if needed
if [ -f requirements.txt ] && grep -q "python_requires" requirements.txt; then
    echo "🧹 Cleaning requirements.txt..."
    grep -v "python_requires" requirements.txt > requirements_clean.txt
    mv requirements_clean.txt requirements.txt
fi

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements-dev.txt

# Create necessary directories
echo "📁 Creating project structure..."
mkdir -p src/{api,core,models,services,integrations,security,utils,schemas,tasks,database}
mkdir -p tests/{unit,integration,fixtures}
mkdir -p logs data config backups

# Create __init__.py files
echo "📝 Creating __init__.py files..."
find src -type d -exec touch {}/__init__.py \;
find tests -type d -exec touch {}/__init__.py \;

# Setup .env file
if [ -f .env.example ] && [ ! -f .env ]; then
    echo "🔐 Creating .env file..."
    cp .env.example .env
    echo "⚠️  Don't forget to update .env with your API keys!"
fi

# Install pre-commit hooks
if command -v pre-commit &> /dev/null; then
    echo "🎣 Installing pre-commit hooks..."
    pre-commit install
fi

# Run initial tests
echo "🧪 Running initial tests..."
pytest tests/ -v || echo "⚠️  Some tests failed (expected on first run)"

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Edit .env and add your API keys"
echo "   2. Run tests: pytest tests/"
echo "   3. Start development: uvicorn src.api.server:app --reload"
echo ""
