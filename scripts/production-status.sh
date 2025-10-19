#!/bin/bash

# Check production deployment status
# Usage: ./scripts/production-status.sh

ENV_FILE=".env.production"

if [[ ! -f "$ENV_FILE" ]]; then
    echo "Error: $ENV_FILE not found. Run deploy-production.sh first."
    exit 1
fi

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo "=================================================="
echo "CulicidaeLab Production Status"
echo "=================================================="

# Load environment variables
source "$ENV_FILE"

echo -e "${CYAN}Domain:${NC} $DOMAIN"
echo -e "${CYAN}Version:${NC} $VERSION"
echo ""

# Check container status
echo "Container Status:"
docker-compose -f docker-compose.prebuilt.yml --env-file "$ENV_FILE" ps

echo ""
echo "Health Checks:"

# Test endpoints
if curl -s -f "${CLIENT_BACKEND_URL}/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Health endpoint: ${CLIENT_BACKEND_URL}/health"
else
    echo -e "${RED}✗${NC} Health endpoint: ${CLIENT_BACKEND_URL}/health"
fi

if curl -s -f "${CLIENT_BACKEND_URL}/api/species" > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} API endpoint: ${CLIENT_BACKEND_URL}/api/species"
else
    echo -e "${RED}✗${NC} API endpoint: ${CLIENT_BACKEND_URL}/api/species"
fi

if curl -s -f "${CLIENT_BACKEND_URL}/static/images/test-image.txt" > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Static files: ${CLIENT_BACKEND_URL}/static/images/test-image.txt"
else
    echo -e "${YELLOW}⚠${NC} Static files: ${CLIENT_BACKEND_URL}/static/images/test-image.txt"
fi

echo ""
echo "Resource Usage:"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}" $(docker-compose -f docker-compose.prebuilt.yml --env-file "$ENV_FILE" ps -q)

echo ""
echo "Recent Logs (last 10 lines):"
docker-compose -f docker-compose.prebuilt.yml --env-file "$ENV_FILE" logs --tail=10