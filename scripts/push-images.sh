#!/bin/bash
# Push Docker images to registry
# Usage: ./scripts/push-images.sh [version] [registry]

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

if [ -z "$REGISTRY" ]; then
    echo -e "${RED}Error: Registry URL is required${NC}"
    echo "Usage: $0 [version] <registry>"
    echo "Example: $0 v1.0.0 your-registry.com/your-username"
    exit 1
fi

echo -e "${GREEN}Pushing CulicidaeLab images to ${REGISTRY}...${NC}"

# Function to push image
push_image() {
    local service=$1
    
    echo -e "${YELLOW}Pushing ${service}...${NC}"
    
    # Push versioned tag
    docker push "${REGISTRY}/${PROJECT_NAME}-${service}:${VERSION}"
    
    # Push latest tag
    docker push "${REGISTRY}/${PROJECT_NAME}-${service}:latest"
    
    echo -e "${GREEN}✓ ${service} pushed successfully${NC}"
}

# Push all images
push_image "backend"
push_image "frontend"
push_image "nginx"

echo -e "${GREEN}All images pushed successfully to ${REGISTRY}!${NC}"