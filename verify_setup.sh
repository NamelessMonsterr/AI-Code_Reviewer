#!/bin/bash

echo "🔍 Verifying project setup..."

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check requirements.txt
echo -e "\n📄 Checking requirements.txt..."
if [ -f requirements.txt ]; then
    if grep -q "python_requires" requirements.txt; then
        echo -e "${RED}❌ ERROR: requirements.txt contains 'python_requires'${NC}"
        echo "   Run: grep -v 'python_requires' requirements.txt > temp.txt && mv temp.txt requirements.txt"
    else
        echo -e "${GREEN}✅ requirements.txt is clean${NC}"
    fi
else
    echo -e "${RED}❌ ERROR: requirements.txt not found${NC}"
fi

# Check __init__.py files
echo -e "\n📁 Checking __init__.py files..."
required_dirs=("src" "src/api" "src/core" "src/models" "src/services" "src/integrations" "src/security" "src/utils" "tests")
missing_init=0

for dir in "${required_dirs[@]}"; do
    if [ -d "$dir" ]; then
        if [ ! -f "$dir/__init__.py" ]; then
            echo -e "${RED}❌ Missing: $dir/__init__.py${NC}"
            missing_init=$((missing_init + 1))
        fi
    fi
done

if [ $missing_init -eq 0 ]; then
    echo -e "${GREEN}✅ All __init__.py files present${NC}"
else
    echo -e "${YELLOW}⚠️  Found $missing_init missing __init__.py files${NC}"
fi

# Check .env.example
echo -e "\n🔐 Checking .env.example..."
if [ -f .env.example ]; then
    if grep -q "OPENAI_API_KEY" .env.example; then
        echo -e "${GREEN}✅ .env.example exists and looks good${NC}"
    else
        echo -e "${YELLOW}⚠️  .env.example may be incomplete${NC}"
    fi
else
    echo -e "${RED}❌ ERROR: .env.example not found${NC}"
fi

# Check Python version
echo -e "\n🐍 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "   Current version: $python_version"
if python3 -c 'import sys; exit(0 if sys.version_info >= (3, 10) else 1)'; then
    echo -e "${GREEN}✅ Python 3.10+ detected${NC}"
else
    echo -e "${RED}❌ ERROR: Python 3.10+ required${NC}"
fi

# Check if virtual environment is active
echo -e "\n🌍 Checking virtual environment..."
if [ -n "$VIRTUAL_ENV" ]; then
    echo -e "${GREEN}✅ Virtual environment is active: $VIRTUAL_ENV${NC}"
else
    echo -e "${YELLOW}⚠️  No virtual environment detected${NC}"
    echo "   Recommended: python3 -m venv venv && source venv/bin/activate"
fi

# Check Git
echo -e "\n📦 Checking Git repository..."
if [ -d .git ]; then
    echo -e "${GREEN}✅ Git repository initialized${NC}"
    
    # Check .gitignore
    if [ -f .gitignore ]; then
        if grep -q ".env" .gitignore && grep -q "__pycache__" .gitignore; then
            echo -e "${GREEN}✅ .gitignore looks good${NC}"
        else
            echo -e "${YELLOW}⚠️  .gitignore may be incomplete${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  .gitignore not found${NC}"
    fi
else
    echo -e "${RED}❌ Not a Git repository${NC}"
fi

# Check GitHub Actions
echo -e "\n⚙️  Checking GitHub Actions..."
if [ -f .github/workflows/ci.yml ]; then
    echo -e "${GREEN}✅ CI/CD workflow found${NC}"
else
    echo -e "${YELLOW}⚠️  GitHub Actions workflow not found${NC}"
fi

# Summary
echo -e "\n" 
echo "======================================"
echo "           SETUP SUMMARY"
echo "======================================"
echo ""

if [ $missing_init -eq 0 ] && [ -f requirements.txt ] && ! grep -q "python_requires" requirements.txt 2>/dev/null; then
    echo -e "${GREEN}✅ Your setup looks good!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Install dependencies: pip install -r requirements-dev.txt"
    echo "2. Copy environment: cp .env.example .env"
    echo "3. Run tests: pytest tests/"
    echo "4. Commit changes: git add . && git commit -m 'fix: setup corrections'"
else
    echo -e "${YELLOW}⚠️  Some issues need attention (see above)${NC}"
    echo ""
    echo "Quick fixes:"
    echo "1. Create missing __init__.py: find src -type d -exec touch {}/__init__.py \;"
    echo "2. Clean requirements.txt: grep -v 'python_requires' requirements.txt > temp.txt && mv temp.txt requirements.txt"
fi

echo ""
