import docker
import yaml
from typing import Dict

class SelfHostedDeployment:
    """Deploy and manage self-hosted instances"""
    
    def __init__(self):
        self.docker_client = docker.from_env()
    
    def generate_docker_compose(self) -> str:
        """Generate Docker Compose configuration"""
        compose = """
version: '3.8'

services:
  ai-review-bot:
    build: .
    container_name: ai-code-review-bot
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - CLAUDE_API_KEY=${CLAUDE_API_KEY}
      - DATABASE_URL=${DATABASE_URL}
    ports:
      - "8080:8080"
    volumes:
      - ./config:/app/config
      - ./data:/app/data
    restart: unless-stopped
    networks:
      - review-network
  
  postgres:
    image: postgres:14
    container_name: review-bot-db
    environment:
      POSTGRES_DB: review_bot
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - review-network
  
  redis:
    image: redis:7-alpine
    container_name: review-bot-cache
    volumes:
      - redis_data:/data
    networks:
      - review-network

volumes:
  postgres_data:
  redis_data:

networks:
  review-network:
    driver: bridge
"""
        return compose
    
    def generate_kubernetes_config(self) -> str:
        """Generate Kubernetes deployment config"""
        k8s_config = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-code-review-bot
  labels:
    app: review-bot
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
              name: ai-secrets
              key: openai-key
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
---
apiVersion: v1
kind: Service
metadata:
  name: review-bot-service
spec:
  selector:
    app: review-bot
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8080
  type: LoadBalancer
"""
        return k8s_config
    
    def deploy_with_docker(self):
        """Deploy using Docker"""
        dockerfile = """
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY config/ ./config/

EXPOSE 8080

CMD ["python", "-m", "src.api.server"]
"""
        with open('Dockerfile', 'w') as f:
            f.write(dockerfile)
        
        # Build image
        image, logs = self.docker_client.images.build(path='.', tag='ai-review-bot:latest')
        return image
