#!/bin/bash
# Run SmartSupport AI Docker containers

set -e

echo "========================================"
echo "SmartSupport AI - Docker Run Script"
echo "========================================"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
MODE="${1:-dev}"
COMPOSE_FILE="docker-compose.yml"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${RED}✗ .env file not found!${NC}"
    echo "Creating .env from .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${YELLOW}⚠ Please update .env with your API keys${NC}"
    else
        echo -e "${RED}✗ .env.example not found!${NC}"
        exit 1
    fi
fi

# Select compose file based on mode
if [ "$MODE" = "prod" ] || [ "$MODE" = "production" ]; then
    COMPOSE_FILE="docker-compose.prod.yml"
    echo -e "${YELLOW}Running in PRODUCTION mode${NC}"
else
    echo -e "${YELLOW}Running in DEVELOPMENT mode${NC}"
fi

# Stop existing containers
echo ""
echo -e "${YELLOW}Stopping existing containers...${NC}"
docker-compose -f $COMPOSE_FILE down

# Start containers
echo ""
echo -e "${YELLOW}Starting containers...${NC}"
docker-compose -f $COMPOSE_FILE up -d

# Wait for services to be healthy
echo ""
echo -e "${YELLOW}Waiting for services to be healthy...${NC}"
sleep 5

# Check service status
echo ""
echo -e "${YELLOW}Service Status:${NC}"
docker-compose -f $COMPOSE_FILE ps

# Show logs
echo ""
echo -e "${GREEN}✓ Containers started successfully!${NC}"
echo ""
echo "Application URL: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo -e "${YELLOW}To view logs:${NC}"
echo "  docker-compose -f $COMPOSE_FILE logs -f"
echo ""
echo -e "${YELLOW}To stop containers:${NC}"
echo "  docker-compose -f $COMPOSE_FILE down"
echo ""
echo -e "${YELLOW}To restart:${NC}"
echo "  docker-compose -f $COMPOSE_FILE restart"

echo "========================================"
