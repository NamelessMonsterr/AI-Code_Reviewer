echo "📊 System Monitoring"
echo ""

# Show container status
echo "=== Container Status ==="
docker-compose ps
echo ""

# Show resource usage
echo "=== Resource Usage ==="
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
echo ""

# Show recent logs
echo "=== Recent Logs ==="
docker-compose logs --tail=20 ai-review-bot
echo ""

# Show health status
echo "=== Health Check ==="
curl -s http://localhost:8080/health | python3 -m json.tool
echo ""

# Show rate limit status
echo "=== Rate Limits ==="
curl -s http://localhost:8080/api/status | python3 -m json.tool


# ============================================
# FILE: Makefile
# ============================================
.PHONY: help setup install test lint clean docker-build docker-up docker-down deploy backup restore

help:
	@echo "AI Code Review Bot - Makefile Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make setup          - Initial setup"
	@echo "  make install        - Install dependencies"
	@echo ""
	@echo "Development:"
	@echo "  make test           - Run tests"
	@echo "  make lint           - Run linters"
	@echo "  make clean          - Clean build artifacts"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build   - Build Docker image"
	@echo "  make docker-up      - Start containers"
	@echo "  make docker-down    - Stop containers"
	@echo "  make docker-logs    - View logs"
	@echo ""
	@echo "Operations:"
	@echo "  make deploy         - Deploy to staging"
	@echo "  make backup         - Create backup"
	@echo "  make restore        - Restore from backup"
	@echo "  make monitor        - Monitor system"

setup:
	@./scripts/setup.sh

install:
	@pip install -r requirements.txt

test:
	@./scripts/test.sh

lint:
	@./scripts/lint.sh

clean:
	@echo "Cleaning build artifacts..."
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@rm -rf .pytest_cache .coverage htmlcov/ dist/ build/
	@echo "✅ Clean complete"

docker-build:
	@docker-compose build

docker-up:
	@docker-compose up -d
	@echo "Waiting for services to be ready..."
	@sleep 5
	@docker-compose ps

docker-down:
	@docker-compose down

docker-logs:
	@docker-compose logs -f

deploy:
	@./scripts/deploy.sh staging

deploy-prod:
	@./scripts/deploy.sh production

backup:
	@./scripts/backup.sh

restore:
	@./scripts/restore.sh

monitor:
	@./scripts/monitor.sh

validate:
	@./scripts/validate-config.sh
