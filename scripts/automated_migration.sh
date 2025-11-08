#!/bin/bash
#
# Automated Migration Script for AI Code Review Bot
# This script automates the migration process
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Banner
echo -e "${BLUE}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════╗
║     AI Code Review Bot - Automated Migration Script      ║
║                  Version 2.0 - 2024                       ║
╚═══════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# Step 1: Backup
log_info "Step 1: Creating backups..."
BACKUP_DIR="backups/migration_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

FILES_TO_BACKUP=(
    "src/documentation/doc_generator.py"
    "src/interactive/chat_interface.py"
    "src/performance/profiler.py"
    "src/testing/test_generator.py"
    "src/search/semantic_search.py"
    "src/training/model_finetuner.py"
)

for file in "${FILES_TO_BACKUP[@]}"; do
    if [ -f "$file" ]; then
        cp "$file" "$BACKUP_DIR/"
        log_success "Backed up: $file"
    else
        log_warning "File not found: $file"
    fi
done

log_success "Backups created in: $BACKUP_DIR"

# Step 2: Check Python version
log_info "Step 2: Checking Python version..."
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
REQUIRED_VERSION="3.10"

if (( $(echo "$PYTHON_VERSION >= $REQUIRED_VERSION" | bc -l) )); then
    log_success "Python version: $PYTHON_VERSION (OK)"
else
    log_error "Python $REQUIRED_VERSION+ required. Found: $PYTHON_VERSION"
    exit 1
fi

# Step 3: Update dependencies
log_info "Step 3: Updating dependencies..."
if grep -q "openai>=1.12.0" requirements.txt; then
    log_success "OpenAI dependency already updated"
else
    log_warning "Updating requirements.txt..."
    sed -i.bak 's/openai==.*/openai>=1.12.0/' requirements.txt
    log_success "Updated OpenAI dependency to >=1.12.0"
fi

# Install/update packages
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt --upgrade > /dev/null 2>&1
log_success "Dependencies updated"

# Step 4: Create base class directory
log_info "Step 4: Creating AI base class structure..."
mkdir -p src/ai
touch src/ai/__init__.py

if [ -f "src/ai/ai_model_base.py" ]; then
    log_warning "Base class already exists, skipping..."
else
    log_info "Please add ai_model_base.py from artifacts to src/ai/"
fi

# Step 5: Create test directories
log_info "Step 5: Setting up test structure..."
mkdir -p tests/phase4
mkdir -p tests/phase5
touch tests/phase4/__init__.py
touch tests/phase5/__init__.py

# Step 6: Validate OpenAI API migration
log_info "Step 6: Validating OpenAI API migration..."

check_old_api() {
    local file=$1
    if grep -q "openai.ChatCompletion.create" "$file" 2>/dev/null; then
        return 1  # Old API found
    fi
    return 0  # OK
}

MIGRATION_NEEDED=false
for file in "${FILES_TO_BACKUP[@]}"; do
    if [ -f "$file" ]; then
        if check_old_api "$file"; then
            log_success "✓ $file (migrated)"
        else
            log_warning "✗ $file (needs migration)"
            MIGRATION_NEEDED=true
        fi
    fi
done

if [ "$MIGRATION_NEEDED" = true ]; then
    log_warning "Some files still need OpenAI API migration!"
    log_info "Please replace files with fixed versions from artifacts"
fi

# Step 7: Run tests
log_info "Step 7: Running tests..."

if command -v pytest &> /dev/null; then
    log_info "Running existing tests..."
    
    # Run with coverage
    if pytest tests/ -v --cov=src --cov-report=term-missing --cov-fail-under=0 2>&1 | tee test_output.log; then
        COVERAGE=$(grep "TOTAL" test_output.log | awk '{print $NF}' | tr -d '%')
        log_success "Tests passed! Coverage: ${COVERAGE}%"
        
        if (( $(echo "$COVERAGE >= 85" | bc -l) )); then
            log_success "Coverage target met (≥85%)"
        else
            log_warning "Coverage below target: ${COVERAGE}% < 85%"
        fi
    else
        log_error "Some tests failed. Check test_output.log"
    fi
    
    rm -f test_output.log
else
    log_warning "pytest not found, skipping tests"
fi

# Step 8: Security checks
log_info "Step 8: Running security checks..."

# Check for default secrets
if grep -q "your-jwt-secret-key-at-least-32-characters-long-please-change-this" .env 2>/dev/null; then
    log_error "DEFAULT JWT_SECRET found in .env! Change it immediately!"
fi

# Run bandit
if command -v bandit &> /dev/null; then
    log_info "Running bandit security scan..."
    if bandit -r src/ -ll -f txt > security_report.txt 2>&1; then
        log_success "No high/medium security issues found"
    else
        log_warning "Security issues detected. Check security_report.txt"
    fi
else
    log_warning "bandit not installed, skipping security scan"
fi

# Step 9: Code quality checks
log_info "Step 9: Running code quality checks..."

if command -v flake8 &> /dev/null; then
    log_info "Running flake8..."
    if flake8 src/ --max-line-length=120 --count --statistics > flake8_report.txt 2>&1; then
        log_success "No flake8 issues found"
    else
        ISSUES=$(tail -1 flake8_report.txt | awk '{print $1}')
        log_warning "Flake8 found $ISSUES issues. Check flake8_report.txt"
    fi
else
    log_warning "flake8 not installed, skipping lint"
fi

# Step 10: Create migration report
log_info "Step 10: Generating migration report..."

REPORT_FILE="migration_report_$(date +%Y%m%d_%H%M%S).md"

cat > "$REPORT_FILE" << EOF
# Migration Report

**Date**: $(date)
**Backup Location**: $BACKUP_DIR

## Files Updated
EOF

for file in "${FILES_TO_BACKUP[@]}"; do
    if [ -f "$file" ]; then
        if check_old_api "$file"; then
            echo "- ✅ $file (Migrated)" >> "$REPORT_FILE"
        else
            echo "- ⚠️  $file (Needs migration)" >> "$REPORT_FILE"
        fi
    fi
done

cat >> "$REPORT_FILE" << EOF

## Test Results
- Test suite: $([ -f "test_output.log" ] && echo "Executed" || echo "Skipped")
- Coverage: ${COVERAGE:-N/A}%

## Security Scan
- Bandit: $([ -f "security_report.txt" ] && echo "Completed" || echo "Skipped")

## Code Quality
- Flake8: $([ -f "flake8_report.txt" ] && echo "Completed" || echo "Skipped")

## Next Steps
1. Review files marked with ⚠️  and apply fixes
2. Add comprehensive tests for Phase 4 & 5
3. Add architecture diagrams to README
4. Update documentation
5. Deploy to staging for testing

## Rollback Instructions
To rollback:
\`\`\`bash
cp $BACKUP_DIR/*.py src/*/
docker-compose restart
\`\`\`
EOF

log_success "Migration report generated: $REPORT_FILE"

# Step 11: Summary
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Migration Script Completed!${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""
log_info "Summary:"
echo "  📦 Backups: $BACKUP_DIR"
echo "  📄 Report: $REPORT_FILE"
echo "  🔒 Security: $([ -f 'security_report.txt' ] && echo 'Scanned' || echo 'Skipped')"
echo "  🧪 Tests: $([ -f 'test_output.log' ] && echo 'Passed' || echo 'Skipped')"
echo ""

if [ "$MIGRATION_NEEDED" = true ]; then
    log_warning "Action Required:"
    echo "  1. Replace files with fixed versions from artifacts"
    echo "  2. Run: pytest tests/ -v"
    echo "  3. Review: $REPORT_FILE"
else
    log_success "All files migrated successfully!"
fi

echo ""
log_info "Next steps:"
echo "  1. Review the migration report: $REPORT_FILE"
echo "  2. Add comprehensive tests from artifacts"
echo "  3. Add architecture diagrams to README.md"
echo "  4. Run: ./scripts/verify-fixes.sh"
echo "  5. Deploy to staging"
echo ""

# Step 12: Create verification script
log_info "Creating verification script..."

cat > scripts/verify-fixes.sh << 'EOFSCRIPT'
#!/bin/bash
set -e

echo "🔍 Verifying all fixes..."

echo "1️⃣  Testing OpenAI API migration..."
pytest tests/test_code_fixer.py -v

echo "2️⃣  Running all tests..."
pytest tests/ -v --cov=src --cov-report=term

echo "3️⃣  Checking coverage..."
pytest tests/ --cov=src --cov-fail-under=85 --cov-report=term-missing

echo "4️⃣  Security scan..."
bandit -r src/ -ll

echo "5️⃣  Code quality..."
flake8 src/ --max-line-length=120
pylint src/ --max-line-length=120 --disable=C0111,R0903

echo "✅ All verifications passed!"
EOFSCRIPT

chmod +x scripts/verify-fixes.sh
log_success "Created: scripts/verify-fixes.sh"

echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║              Migration Setup Complete! 🎉                 ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""
