#!/bin/bash
# Build Docker images for SmartSupport AI

set -e

echo "========================================"
echo "SmartSupport AI - Docker Build Script"
echo "========================================"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
IMAGE_NAME="smartsupport-ai"
TAG="${1:-latest}"
BUILD_ENV="${2:-development}"

echo -e "${YELLOW}Building Docker image...${NC}"
echo "Image: $IMAGE_NAME:$TAG"
echo "Environment: $BUILD_ENV"
echo "========================================"

# Build the image
if [ "$BUILD_ENV" = "production" ]; then
    echo -e "${YELLOW}Building production image...${NC}"
    docker build \
        --build-arg BUILD_ENV=production \
        --tag $IMAGE_NAME:$TAG \
        --tag $IMAGE_NAME:latest \
        --file Dockerfile \
        .
else
    echo -e "${YELLOW}Building development image...${NC}"
    docker build \
        --tag $IMAGE_NAME:$TAG \
        --tag $IMAGE_NAME:dev \
        --file Dockerfile \
        .
fi

# Check if build was successful
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Docker image built successfully!${NC}"
    echo ""
    echo "Image details:"
    docker images | grep $IMAGE_NAME
    echo ""
    echo -e "${GREEN}To run the container:${NC}"
    echo "  ./scripts/docker-run.sh"
    echo ""
    echo -e "${GREEN}To run with docker-compose:${NC}"
    echo "  docker-compose up -d"
else
    echo -e "${RED}✗ Docker build failed!${NC}"
    exit 1
fi

echo "========================================"
echo -e "${GREEN}Build complete!${NC}"
echo "========================================"
