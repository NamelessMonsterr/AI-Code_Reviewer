#!/bin/bash
set -e

echo "🚀 Setting up AI Code Review Bot..."
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ All prerequisites satisfied${NC}"
echo ""

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    
    # Generate secrets
    JWT_SECRET=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
    DB_PASSWORD=$(python3 -c 'import secrets; print(secrets.token_urlsafe(16))')
    
    # Update .env
    sed -i "s/your-jwt-secret-key-at-least-32-characters-long-please-change-this/$JWT_SECRET/" .env
    sed -i "s/your-secure-database-password-here/$DB_PASSWORD/" .env
    
    echo -e "${YELLOW}⚠️  Please edit .env and add your OPENAI_API_KEY${NC}"
    echo ""
fi

# Create required directories
echo "📁 Creating directories..."
mkdir -p data logs config monitoring/prometheus monitoring/grafana

# Install Python dependencies
echo "📦 Installing Python dependencies..."
python3 -m pip install -r requirements.txt

# Validate configuration
echo "🔍 Validating configuration..."
if python3 -m src.config.validator; then
    echo -e "${GREEN}✅ Configuration valid${NC}"
else
    echo -e "${RED}❌ Configuration validation failed${NC}"
    exit 1
fi

# Build Docker image
echo "🐳 Building Docker image..."
docker-compose build

echo ""
echo -e "${GREEN}✅ Setup complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your OPENAI_API_KEY"
echo "2. Run: docker-compose up -d"
echo "3. Check status: docker-compose ps"
echo "4. View logs: docker-compose logs -f"


# ============================================
# FILE: scripts/migrate-openai-api.sh
# ============================================
#!/bin/bash
set -e

echo "🔄 Migrating to new OpenAI API..."
echo ""

FILES_TO_MIGRATE=(
    "src/documentation/doc_generator.py"
    "src/interactive/chat_interface.py"
    "src/performance/profiler.py"
    "src/testing/test_generator.py"
    "src/search/semantic_search.py"
    "src/training/model_finetuner.py"
)

echo "Files to migrate:"
for file in "${FILES_TO_MIGRATE[@]}"; do
    echo "  - $file"
done
echo ""

read -p "Continue with migration? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Migration cancelled"
    exit 1
fi

# Backup original files
echo "📦 Creating backups..."
for file in "${FILES_TO_MIGRATE[@]}"; do
    if [ -f "$file" ]; then
        cp "$file" "$file.backup"
        echo "  ✓ Backed up $file"
    fi
done
echo ""

# Apply migrations (files are already fixed in the artifact above)
echo "✨ Applying migrations..."
echo "Please replace the content of the following files with the fixed versions provided:"
for file in "${FILES_TO_MIGRATE[@]}"; do
    echo "  - $file"
done
echo ""

echo "Backups are available at: *.backup"
echo "Run tests after migration: pytest tests/"
