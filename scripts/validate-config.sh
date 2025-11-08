#!/bin/bash

echo "🔍 Validating environment configuration..."
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "📝 Creating .env from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your actual values"
    exit 1
fi

# Source .env
set -a
source .env
set +a

# Validate required variables
REQUIRED_VARS=(
    "OPENAI_API_KEY"
    "JWT_SECRET"
    "DB_PASSWORD"
)

MISSING_VARS=()

for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        MISSING_VARS+=("$var")
    fi
done

if [ ${#MISSING_VARS[@]} -ne 0 ]; then
    echo "❌ Missing required environment variables:"
    for var in "${MISSING_VARS[@]}"; do
        echo "   - $var"
    done
    exit 1
fi

# Validate JWT_SECRET length
if [ ${#JWT_SECRET} -lt 32 ]; then
    echo "❌ JWT_SECRET must be at least 32 characters long"
    echo "💡 Generate with: python -c 'import secrets; print(secrets.token_hex(32))'"
    exit 1
fi

# Validate OpenAI API key format
if [[ ! $OPENAI_API_KEY =~ ^sk- ]]; then
    echo "❌ OPENAI_API_KEY must start with 'sk-'"
    exit 1
fi

# Run Python validation
echo "Running detailed validation..."
python -m src.config.validator

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ All validations passed!"
    exit 0
else
    echo ""
    echo "❌ Validation failed"
    exit 1
fi