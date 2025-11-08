# Deployment Guide - AI Code Review Bot

Complete guide for deploying the AI Code Review Bot to production environments.

## Table of Contents
1. [Quick Start](#quick-start)
2. [Docker Deployment](#docker-deployment)
3. [Kubernetes Deployment](#kubernetes-deployment)
4. [Self-Hosted Setup](#self-hosted-setup)
5. [Environment Configuration](#environment-configuration)
6. [Scaling & Performance](#scaling--performance)
7. [Monitoring & Logs](#monitoring--logs)
8. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Prerequisites
- Docker 20.10+
- Kubernetes 1.24+ (for K8s deployment)
- Python 3.10+
- Node.js 18+ (for GitHub Action)
- At least 4GB RAM, 2 CPU cores

### Environment Variables Required
```bash
# AI API Keys
OPENAI_API_KEY=sk-...
CLAUDE_API_KEY=sk-ant-...
GOOGLE_AI_KEY=...

# Security
JWT_SECRET=<32+ character secret>

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/review_bot

# GitHub
GITHUB_TOKEN=ghp_...

# Optional
REDIS_URL=redis://localhost:6379
```

---

## Docker Deployment

### Step 1: Create Dockerfile

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY config/ ./config/

# Create data directories
RUN mkdir -p /app/data /app/logs

# Expose API port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080/health')"

CMD ["python", "-m", "src.api.server"]
```

### Step 2: Create docker-compose.yml

```yaml
version: '3.8'

services:
  ai-review-bot:
    build: .
    container_name: ai-code-review-bot
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - CLAUDE_API_KEY=${CLAUDE_API_KEY}
      - DATABASE_URL=postgresql://postgres:${DB_PASSWORD}@postgres:5432/review_bot
      - REDIS_URL=redis://redis:6379
      - JWT_SECRET=${JWT_SECRET}
    ports:
      - "8080:8080"
    volumes:
      - ./config:/app/config
      - ./data:/app/data
      - ./logs:/app/logs
    depends_on:
      - postgres
      - redis
    restart: unless-stopped
    networks:
      - review-network

  postgres:
    image: postgres:14-alpine
    container_name: review-bot-db
    environment:
      POSTGRES_DB: review_bot
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    networks:
      - review-network
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    container_name: review-bot-cache
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    networks:
      - review-network
    restart: unless-stopped

  # Optional: Monitoring
  prometheus:
    image: prom/prometheus:latest
    container_name: review-bot-prometheus
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"
    networks:
      - review-network

volumes:
  postgres_data:
  redis_data:
  prometheus_data:

networks:
  review-network:
    driver: bridge
```

### Step 3: Deploy with Docker Compose

```bash
# Create .env file
cat > .env << EOF
OPENAI_API_KEY=your_key_here
CLAUDE_API_KEY=your_key_here
JWT_SECRET=$(python -c 'import secrets; print(secrets.token_hex(32))')
DB_PASSWORD=$(python -c 'import secrets; print(secrets.token_urlsafe(16))')
EOF

# Build and start services
docker-compose up -d

# Check logs
docker-compose logs -f ai-review-bot

# Check health
curl http://localhost:8080/health
```

---

## Kubernetes Deployment

### Step 1: Create Namespace

```bash
kubectl create namespace ai-code-review
```

### Step 2: Create Secrets

```bash
# Create secret for API keys
kubectl create secret generic ai-review-secrets \
  --from-literal=openai-api-key=$OPENAI_API_KEY \
  --from-literal=claude-api-key=$CLAUDE_API_KEY \
  --from-literal=jwt-secret=$JWT_SECRET \
  --from-literal=db-password=$DB_PASSWORD \
  -n ai-code-review
```

### Step 3: Create ConfigMap

```yaml
# config-map.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: ai-review-config
  namespace: ai-code-review
data:
  custom_rules.yaml: |
    naming_conventions:
      python:
        class_name: '^[A-Z][a-zA-Z0-9]*$'
        function_name: '^[a-z_][a-z0-9_]*$'
    max_complexity: 10
    max_line_length: 120
```

Apply:
```bash
kubectl apply -f config-map.yaml
```

### Step 4: Deploy PostgreSQL

```yaml
# postgres-deployment.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  namespace: ai-code-review
spec:
  serviceName: postgres
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:14-alpine
        ports:
        - containerPort: 5432
        env:
        - name: POSTGRES_DB
          value: review_bot
        - name: POSTGRES_USER
          value: postgres
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: ai-review-secrets
              key: db-password
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
  - metadata:
      name: postgres-storage
    spec:
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 10Gi
---
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: ai-code-review
spec:
  selector:
    app: postgres
  ports:
  - port: 5432
  clusterIP: None
```

### Step 5: Deploy Redis

```yaml
# redis-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
  namespace: ai-code-review
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:7-alpine
        ports:
        - containerPort: 6379
        command: ["redis-server", "--appendonly", "yes"]
        volumeMounts:
        - name: redis-storage
          mountPath: /data
      volumes:
      - name: redis-storage
        persistentVolumeClaim:
          claimName: redis-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: redis
  namespace: ai-code-review
spec:
  selector:
    app: redis
  ports:
  - port: 6379
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: redis-pvc
  namespace: ai-code-review
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 5Gi
```

### Step 6: Deploy Application

```yaml
# app-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-review-bot
  namespace: ai-code-review
spec:
  replicas: 3
  selector:
    matchLabels:
      app: review-bot
  template:
    metadata:
      labels:
        app: review-bot
    spec:
      containers:
      - name: review-bot
        image: your-registry/ai-review-bot:latest
        ports:
        - containerPort: 8080
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: ai-review-secrets
              key: openai-api-key
        - name: CLAUDE_API_KEY
          valueFrom:
            secretKeyRef:
              name: ai-review-secrets
              key: claude-api-key
        - name: JWT_SECRET
          valueFrom:
            secretKeyRef:
              name: ai-review-secrets
              key: jwt-secret
        - name: DATABASE_URL
          value: postgresql://postgres:$(DB_PASSWORD)@postgres:5432/review_bot
        - name: REDIS_URL
          value: redis://redis:6379
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 5
        volumeMounts:
        - name: config
          mountPath: /app/config
        - name: data
          mountPath: /app/data
      volumes:
      - name: config
        configMap:
          name: ai-review-config
      - name: data
        persistentVolumeClaim:
          claimName: app-data-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: review-bot-service
  namespace: ai-code-review
spec:
  selector:
    app: review-bot
  type: LoadBalancer
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8080
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: app-data-pvc
  namespace: ai-code-review
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 20Gi
```

### Step 7: Deploy Horizontal Pod Autoscaler

```yaml
# hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: review-bot-hpa
  namespace: ai-code-review
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ai-review-bot
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### Step 8: Deploy Everything

```bash
# Apply all configurations
kubectl apply -f postgres-deployment.yaml
kubectl apply -f redis-deployment.yaml
kubectl apply -f app-deployment.yaml
kubectl apply -f hpa.yaml

# Check deployment status
kubectl get all -n ai-code-review

# Check logs
kubectl logs -f deployment/ai-review-bot -n ai-code-review

# Get service endpoint
kubectl get svc review-bot-service -n ai-code-review
```

---

## Self-Hosted Setup

### On-Premise Installation

```bash
# 1. Install system dependencies
sudo apt-get update
sudo apt-get install -y python3.10 python3-pip postgresql redis-server nginx

# 2. Clone repository
git clone https://github.com/your-org/AI-Code_Reviewer.git
cd AI-Code_Reviewer

# 3. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 4. Install Python dependencies
pip install -r requirements.txt

# 5. Setup database
sudo -u postgres psql << EOF
CREATE DATABASE review_bot;
CREATE USER review_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE review_bot TO review_user;
EOF

# 6. Run database migrations
alembic upgrade head

# 7. Configure systemd service
sudo tee /etc/systemd/system/ai-review-bot.service << EOF
[Unit]
Description=AI Code Review Bot
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/ai-review-bot
Environment="OPENAI_API_KEY=your_key"
Environment="JWT_SECRET=your_secret"
ExecStart=/opt/ai-review-bot/venv/bin/python -m src.api.server
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 8. Start service
sudo systemctl daemon-reload
sudo systemctl enable ai-review-bot
sudo systemctl start ai-review-bot

# 9. Configure Nginx reverse proxy
sudo tee /etc/nginx/sites-available/ai-review-bot << EOF
server {
    listen 80;
    server_name review-bot.example.com;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

sudo ln -s /etc/nginx/sites-available/ai-review-bot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## Scaling & Performance

### Horizontal Scaling
```bash
# Docker Compose
docker-compose up -d --scale ai-review-bot=5

# Kubernetes
kubectl scale deployment ai-review-bot --replicas=5 -n ai-code-review
```

### Performance Tuning

**Redis Caching:**
```python
# Add to src/api/server.py
import redis
cache = redis.Redis(host='redis', port=6379, decode_responses=True)

@app.get("/api/review")
async def review(code: str):
    cache_key = f"review:{hash(code)}"
    cached = cache.get(cache_key)
    if cached:
        return json.loads(cached)
    
    # ... perform review ...
    cache.setex(cache_key, 3600, json.dumps(result))
    return result
```

### Load Balancing

**Nginx Configuration:**
```nginx
upstream review_bot {
    least_conn;
    server review-bot-1:8080;
    server review-bot-2:8080;
    server review-bot-3:8080;
}

server {
    listen 80;
    location / {
        proxy_pass http://review_bot;
    }
}
```

---

## Monitoring & Logs

### Prometheus Metrics

```python
# Add to src/api/server.py
from prometheus_client import Counter, Histogram, generate_latest

review_counter = Counter('reviews_total', 'Total code reviews')
review_duration = Histogram('review_duration_seconds', 'Review duration')

@app.get('/metrics')
async def metrics():
    return Response(generate_latest(), media_type='text/plain')
```

### Centralized Logging

```yaml
# filebeat.yml
filebeat.inputs:
- type: log
  enabled: true
  paths:
    - /app/logs/*.log
  json.keys_under_root: true
  
output.elasticsearch:
  hosts: ["elasticsearch:9200"]
```

### Health Checks

```python
# src/api/health.py
@app.get("/health")
async def health():
    checks = {
        "database": check_database(),
        "redis": check_redis(),
        "openai": check_openai()
    }
    
    status = "healthy" if all(checks.values()) else "unhealthy"
    return {"status": status, "checks": checks}
```

---

## Troubleshooting

### Common Issues

**1. Database Connection Errors**
```bash
# Check connection
psql $DATABASE_URL

# Verify credentials
kubectl get secret ai-review-secrets -n ai-code-review -o yaml
```

**2. Out of Memory**
```bash
# Increase memory limit
kubectl set resources deployment ai-review-bot \
  --limits=memory=4Gi -n ai-code-review
```

**3. API Rate Limits**
- Implement exponential backoff
- Use multiple API keys with round-robin
- Enable caching

**4. Slow Performance**
```bash
# Check metrics
kubectl top pods -n ai-code-review

# Scale up
kubectl scale deployment ai-review-bot --replicas=10
```

### Debug Mode

```bash
# Enable debug logging
docker-compose run -e DEBUG=true ai-review-bot

# Kubernetes
kubectl set env deployment/ai-review-bot DEBUG=true -n ai-code-review
```

---

## Security Best Practices

1. **Use secrets management** (Vault, AWS Secrets Manager)
2. **Enable TLS** for all endpoints
3. **Rotate API keys** regularly
4. **Implement rate limiting**
5. **Use network policies** in Kubernetes
6. **Regular security audits**
7. **Keep dependencies updated**

---

## Backup & Recovery

```bash
# Backup database
kubectl exec -it postgres-0 -n ai-code-review -- \
  pg_dump -U postgres review_bot > backup.sql

# Backup persistent volumes
kubectl get pvc -n ai-code-review
# Use volume snapshots or velero

# Restore
kubectl exec -i postgres-0 -n ai-code-review -- \
  psql -U postgres review_bot < backup.sql
```
