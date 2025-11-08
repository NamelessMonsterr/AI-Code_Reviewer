# 🚀 Quick Start & Cheat Sheet

## 30-Second Setup

```bash
# 1. Clone & enter directory
git clone https://github.com/NamelessMonsterr/AI-Code_Reviewer.git
cd AI-Code_Reviewer

# 2. Set environment variables
export OPENAI_API_KEY="sk-your-key-here"
export JWT_SECRET=$(python -c 'import secrets; print(secrets.token_hex(32))')

# 3. Install & run
pip install -r requirements.txt
docker-compose up -d

# 4. Test
curl http://localhost:8080/health
```

---

## Common Commands

### Local Development
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild after code changes
docker-compose up -d --build

# Run tests
pytest tests/ -v

# Run specific test file
pytest tests/test_feedback_learner.py -v

# Run with coverage
pytest --cov=src --cov-report=html
```

### Review Code
```bash
# Review entire repository
python -m src.enhanced_review .

# Review specific file
python -m src.enhanced_review --file src/main.py

# Review with compliance
python -m src.enhanced_review_phase3 --standards SOC2,HIPAA

# Review with full Phase 5 features
python -m src.enhanced_review_phase5
```

### API Usage
```bash
# Get health status
curl http://localhost:8080/health

# Review code
curl -X POST http://localhost:8080/api/review \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"code": "def hello(): pass", "language": "python"}'

# Get analytics
curl http://localhost:8080/api/analytics/summary \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get compliance status
curl http://localhost:8080/api/compliance/status \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Deployment Commands

### Docker
```bash
# Build image
docker build -t ai-review-bot:latest .

# Run container
docker run -d -p 8080:8080 \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  -e JWT_SECRET=$JWT_SECRET \
  --name ai-review-bot \
  ai-review-bot:latest

# Push to registry
docker tag ai-review-bot:latest ghcr.io/your-org/ai-review-bot:latest
docker push ghcr.io/your-org/ai-review-bot:latest
```

### Kubernetes
```bash
# Create namespace
kubectl create namespace ai-code-review

# Create secrets
kubectl create secret generic ai-review-secrets \
  --from-literal=openai-api-key=$OPENAI_API_KEY \
  --from-literal=jwt-secret=$JWT_SECRET \
  -n ai-code-review

# Deploy
kubectl apply -f k8s/ -n ai-code-review

# Check status
kubectl get all -n ai-code-review

# View logs
kubectl logs -f deployment/ai-review-bot -n ai-code-review

# Scale
kubectl scale deployment ai-review-bot --replicas=5 -n ai-code-review

# Port forward for testing
kubectl port-forward svc/review-bot-service 8080:80 -n ai-code-review
```

---

## Configuration Quick Reference

### Environment Variables
```bash
# Required
OPENAI_API_KEY=sk-...
JWT_SECRET=<32+ chars>

# Optional AI Providers
CLAUDE_API_KEY=sk-ant-...
GOOGLE_AI_KEY=...

# Database
DATABASE_URL=postgresql://user:pass@localhost/db
REDIS_URL=redis://localhost:6379

# Features
ENABLE_AUTO_FIX=true
ENABLE_TEST_GENERATION=true
ENABLE_COMPLIANCE_CHECKS=true

# Logging
LOG_LEVEL=INFO
SENTRY_DSN=...
```

### Custom Rules (config/custom_rules.yaml)
```yaml
naming_conventions:
  python:
    class_name: '^[A-Z][a-zA-Z0-9]*$'
    function_name: '^[a-z_][a-z0-9_]*$'

forbidden_patterns:
  python:
    - 'eval('
    - 'exec('

max_complexity: 10
max_line_length: 120
```

---

## Troubleshooting

### Issue: Can't connect to API
```bash
# Check if service is running
docker ps | grep ai-review

# Check logs
docker logs ai-review-bot

# Verify port
netstat -tulpn | grep 8080

# Test locally
curl http://localhost:8080/health
```

### Issue: Database errors
```bash
# Check database connection
psql $DATABASE_URL

# Reset database
docker-compose down -v
docker-compose up -d

# Run migrations
alembic upgrade head
```

### Issue: OpenAI API errors
```bash
# Verify API key
python -c "import openai; openai.api_key='$OPENAI_API_KEY'; print('OK')"

# Check rate limits
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"

# Test with minimal request
python -c "
from openai import OpenAI
client = OpenAI()
print(client.models.list())
"
```

### Issue: Permission denied
```bash
# Fix file permissions
chmod +x scripts/*.sh

# Fix Docker socket
sudo chmod 666 /var/run/docker.sock

# Fix JWT secret length
python -c "import secrets; print(f'JWT_SECRET={secrets.token_hex(32)}')" >> .env
```

---

## GitHub Actions Setup

### 1. Add Secrets
Go to Settings → Secrets and add:
- `OPENAI_API_KEY`
- `CLAUDE_API_KEY` (optional)
- `AWS_ACCESS_KEY_ID` (for deployment)
- `AWS_SECRET_ACCESS_KEY`
- `SLACK_WEBHOOK` (for notifications)

### 2. Enable Workflows
```bash
# Copy workflow files
cp .github/workflows/*.yml .github/workflows/

# Commit and push
git add .github/workflows/
git commit -m "Add CI/CD workflows"
git push
```

### 3. Monitor
- View workflow runs: Actions tab
- Check deployment: Environments → Production
- View logs: Click on specific job

---

## Performance Tuning

### Redis Caching
```python
# Enable caching in .env
REDIS_URL=redis://localhost:6379
CACHE_TTL=3600
```

### Concurrent Processing
```bash
# Increase workers
WORKERS=4

# In Docker Compose
environment:
  - WORKERS=4
```

### Database Connection Pool
```python
# In config
SQLALCHEMY_POOL_SIZE=20
SQLALCHEMY_MAX_OVERFLOW=40
```

---

## Monitoring

### Prometheus Metrics
```bash
# Access metrics
curl http://localhost:8080/metrics

# Prometheus config
scrape_configs:
  - job_name: 'ai-review-bot'
    static_configs:
      - targets: ['localhost:8080']
```

### Health Checks
```bash
# Liveness probe
curl http://localhost:8080/health

# Readiness probe
curl http://localhost:8080/ready

# Detailed status
curl http://localhost:8080/api/status
```

### Logs
```bash
# Follow logs
docker-compose logs -f ai-review-bot

# Kubernetes logs
kubectl logs -f deployment/ai-review-bot -n ai-code-review

# Search logs
docker logs ai-review-bot 2>&1 | grep ERROR
```

---

## Testing Cheat Sheet

### Unit Tests
```bash
# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_feedback_learner.py::TestFeedbackLearner::test_record_feedback -v

# Run with markers
pytest -m "not integration" -v

# Run failed tests only
pytest --lf -v
```

### Integration Tests
```bash
# Run integration tests
pytest tests/test_full_review_flow.py -v -m integration

# With services
docker-compose up -d
pytest tests/ -m integration -v
```

### Coverage
```bash
# Generate coverage report
pytest --cov=src --cov-report=html

# View report
open htmlcov/index.html

# Coverage for specific module
pytest --cov=src.feedback --cov-report=term
```

---

## Backup & Restore

### Database Backup
```bash
# Backup
docker exec postgres pg_dump -U postgres review_bot > backup.sql

# Kubernetes
kubectl exec postgres-0 -n ai-code-review -- \
  pg_dump -U postgres review_bot > backup.sql
```

### Restore
```bash
# Docker
docker exec -i postgres psql -U postgres review_bot < backup.sql

# Kubernetes
kubectl exec -i postgres-0 -n ai-code-review -- \
  psql -U postgres review_bot < backup.sql
```

### Configuration Backup
```bash
# Backup configs
tar -czf config-backup.tar.gz config/ .env

# Restore
tar -xzf config-backup.tar.gz
```

---

## Security Checklist

- [ ] Rotate API keys every 90 days
- [ ] Use secrets manager (not .env in production)
- [ ] Enable HTTPS/TLS
- [ ] Implement rate limiting
- [ ] Regular dependency updates
- [ ] Security scans enabled
- [ ] Audit logs reviewed weekly
- [ ] Backup strategy in place
- [ ] Disaster recovery plan tested

---

## Useful Links

- **Documentation**: https://docs.ai-review-bot.com
- **API Docs**: http://localhost:8080/docs
- **GitHub**: https://github.com/NamelessMonsterr/AI-Code_Reviewer
- **Issues**: https://github.com/NamelessMonsterr/AI-Code_Reviewer/issues

---

## Getting Help

```bash
# Check version
python -m src --version

# View help
python -m src.enhanced_review --help

# Debug mode
DEBUG=true python -m src.enhanced_review .

# Verbose logging
LOG_LEVEL=DEBUG python -m src.api.server
```

---

**Pro Tips:**
- Use `docker-compose` for local development
- Use Kubernetes for production
- Enable caching for 50% faster reviews
- Run tests before every commit
- Monitor logs regularly
- Keep dependencies updated
- Backup database weekly
