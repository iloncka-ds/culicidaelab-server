#!/bin/bash
# Build and tag Docker images for CulicidaeLab
# Usage: ./scripts/build-images.sh [version] [registry]

set -e

# Default values
VERSION=${1:-latest}
REGISTRY=${2:-""}
PROJECT_NAME="culicidaelab"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Building CulicidaeLab Docker images...${NC}"

# Function to build and tag image
build_and_tag() {
    local service=$1
    local dockerfile=$2
    local context=$3
    
    echo -e "${YELLOW}Building ${service}...${NC}"
    
    # Build the image
    docker build -f "${dockerfile}" -t "${PROJECT_NAME}-${service}:${VERSION}" "${context}"
    
    # Tag for registry if provided
    if [ -n "$REGISTRY" ]; then
        docker tag "${PROJECT_NAME}-${service}:${VERSION}" "${REGISTRY}/${PROJECT_NAME}-${service}:${VERSION}"
        docker tag "${PROJECT_NAME}-${service}:${VERSION}" "${REGISTRY}/${PROJECT_NAME}-${service}:latest"
    fi
    
    echo -e "${GREEN}✓ ${service} built successfully${NC}"
}

# Build backend
build_and_tag "backend" "backend/Dockerfile" "."

# Build frontend
build_and_tag "frontend" "frontend/Dockerfile" "."

# Build nginx
build_and_tag "nginx" "nginx/Dockerfile" "."

echo -e "${GREEN}All images built successfully!${NC}"

# Show built images
echo -e "${YELLOW}Built images:${NC}"
docker images | grep "${PROJECT_NAME}"

if [ -n "$REGISTRY" ]; then
    echo -e "${YELLOW}Registry images:${NC}"
    docker images | grep "${REGISTRY}/${PROJECT_NAME}"
fi