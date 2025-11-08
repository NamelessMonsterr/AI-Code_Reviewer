#!/bin/bash
set -e

ENVIRONMENT=${1:-staging}

echo "🚀 Deploying to $ENVIRONMENT..."
echo ""

# Validate configuration
echo "Validating configuration..."
./scripts/validate-config.sh

# Run tests
echo "Running tests..."
./scripts/test.sh

# Build Docker image
echo "Building Docker image..."
docker-compose build

# Tag image
IMAGE_TAG="ai-review-bot:${ENVIRONMENT}-$(date +%Y%m%d-%H%M%S)"
docker tag ai-review-bot:latest "$IMAGE_TAG"

echo "Tagged image: $IMAGE_TAG"

if [ "$ENVIRONMENT" = "production" ]; then
    echo ""
    echo "⚠️  PRODUCTION DEPLOYMENT"
    echo "This will deploy to production!"
    read -p "Are you sure? (yes/no) " -r
    echo
    if [[ ! $REPLY = "yes" ]]; then
        echo "Deployment cancelled"
        exit 1
    fi
    
    # Deploy to production
    docker-compose --profile production up -d
else
    # Deploy to staging
    docker-compose up -d
fi

echo ""
echo "✅ Deployment complete!"
echo ""
echo "Check status:"
echo "  docker-compose ps"
echo ""
echo "View logs:"
echo "  docker-compose logs -f ai-review-bot"
