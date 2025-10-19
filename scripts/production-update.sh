#!/bin/bash

# Update production deployment
# Usage: ./scripts/production-update.sh [version]

ENV_FILE=".env.production"

if [[ ! -f "$ENV_FILE" ]]; then
    echo "Error: $ENV_FILE not found. Run deploy-production.sh first."
    exit 1
fi

# Load current environment
source "$ENV_FILE"

# Use provided version or current version
NEW_VERSION=${1:-$VERSION}

echo "Updating CulicidaeLab production deployment..."
echo "Current version: $VERSION"
echo "New version: $NEW_VERSION"
echo ""

# Update version in env file if different
if [[ "$NEW_VERSION" != "$VERSION" ]]; then
    sed -i "s/VERSION=$VERSION/VERSION=$NEW_VERSION/" "$ENV_FILE"
    echo "Updated version in $ENV_FILE"
fi

# Pull new images
echo "Pulling new images..."
docker-compose -f docker-compose.prebuilt.yml --env-file "$ENV_FILE" pull

# Restart services with new images
echo "Restarting services..."
docker-compose -f docker-compose.prebuilt.yml --env-file "$ENV_FILE" up -d

echo "Waiting for services to start..."
sleep 10

# Check status
echo "Checking service status..."
docker-compose -f docker-compose.prebuilt.yml --env-file "$ENV_FILE" ps

echo ""
echo "Update completed!"
echo "Check logs if needed: ./scripts/production-logs.sh"