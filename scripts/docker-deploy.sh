#!/bin/bash
# Deploy SmartSupport AI to production

set -e

echo "========================================"
echo "SmartSupport AI - Production Deployment"
echo "========================================"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT="${1:-production}"
VERSION="${2:-latest}"

echo -e "${BLUE}Deployment Configuration:${NC}"
echo "Environment: $ENVIRONMENT"
echo "Version: $VERSION"
echo "========================================"

# Pre-deployment checks
echo -e "${YELLOW}Running pre-deployment checks...${NC}"

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${RED}✗ .env file not found!${NC}"
    exit 1
fi

# Check if required API keys are set
if ! grep -q "GROQ_API_KEY=" .env || ! grep -q "OPENAI_API_KEY=" .env; then
    echo -e "${RED}✗ API keys not configured in .env!${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Pre-deployment checks passed${NC}"
echo ""

# Build production image
echo -e "${YELLOW}Building production image...${NC}"
./scripts/docker-build.sh $VERSION production

# Run database migrations (if any)
echo ""
echo -e "${YELLOW}Running database migrations...${NC}"
# Add migration commands here if you have them

# Pull latest images for dependencies
echo ""
echo -e "${YELLOW}Pulling dependency images...${NC}"
docker-compose -f docker-compose.prod.yml pull postgres redis nginx

# Stop old containers
echo ""
echo -e "${YELLOW}Stopping old containers...${NC}"
docker-compose -f docker-compose.prod.yml down

# Start new containers
echo ""
echo -e "${YELLOW}Starting new containers...${NC}"
docker-compose -f docker-compose.prod.yml up -d

# Wait for services
echo ""
echo -e "${YELLOW}Waiting for services to be healthy...${NC}"
sleep 10

# Health check
echo ""
echo -e "${YELLOW}Running health checks...${NC}"
HEALTH_CHECK=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/health || echo "000")

if [ "$HEALTH_CHECK" = "200" ]; then
    echo -e "${GREEN}✓ Health check passed${NC}"
else
    echo -e "${RED}✗ Health check failed (HTTP $HEALTH_CHECK)${NC}"
    echo -e "${YELLOW}Check logs with: docker-compose -f docker-compose.prod.yml logs${NC}"
    exit 1
fi

# Show running containers
echo ""
echo -e "${YELLOW}Running containers:${NC}"
docker-compose -f docker-compose.prod.yml ps

# Deployment summary
echo ""
echo "========================================"
echo -e "${GREEN}✓ Deployment successful!${NC}"
echo "========================================"
echo ""
echo "Application URL: http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
echo ""
echo -e "${YELLOW}Useful commands:${NC}"
echo "  View logs:      docker-compose -f docker-compose.prod.yml logs -f"
echo "  Stop services:  docker-compose -f docker-compose.prod.yml down"
echo "  Restart:        docker-compose -f docker-compose.prod.yml restart"
echo "  Status:         docker-compose -f docker-compose.prod.yml ps"
echo ""
echo -e "${BLUE}Monitoring:${NC}"
echo "  Health:         curl http://localhost:8000/api/v1/health"
echo "  Stats:          curl http://localhost:8000/api/v1/stats"
echo ""
echo "========================================"
