#!/bin/bash

# Build nginx with SSL/certbot support
# Usage: ./scripts/build-nginx-ssl.sh [version] [registry]

set -e

VERSION=${1:-latest}
REGISTRY=${2:-}

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}Building nginx with SSL support...${NC}"
echo "Version: $VERSION"
echo "Registry: ${REGISTRY:-local}"

# Build the image
IMAGE_NAME="${REGISTRY}culicidaelab-nginx-ssl:$VERSION"

echo -e "${YELLOW}Building $IMAGE_NAME...${NC}"

docker build \
    -f nginx/Dockerfile.with-certbot \
    -t "$IMAGE_NAME" \
    .

if [[ $? -eq 0 ]]; then
    echo -e "${GREEN}✓ Successfully built $IMAGE_NAME${NC}"
    
    # Show image info
    echo -e "${CYAN}Image details:${NC}"
    docker images "$IMAGE_NAME" --format "table {{.Repository}}\t{{.Tag}}\t{{.ID}}\t{{.CreatedAt}}\t{{.Size}}"
    
    if [[ -n "$REGISTRY" ]]; then
        echo ""
        echo -e "${YELLOW}To push to registry:${NC}"
        echo "docker push $IMAGE_NAME"
    fi
    
    echo ""
    echo -e "${CYAN}To test the image:${NC}"
    echo "docker run --rm -p 80:80 -p 443:443 -e DOMAIN=localhost -e SSL_ENABLED=false $IMAGE_NAME"
    
else
    echo -e "${RED}✗ Failed to build $IMAGE_NAME${NC}"
    exit 1
fi