#!/bin/bash

# Restart containers with SSL configuration
# Usage: ./scripts/restart-with-ssl.sh

set -e

echo "Stopping containers..."
docker-compose -f docker-compose.prebuilt.yml down

echo "Rebuilding nginx image..."
docker build -f nginx/Dockerfile.with-certbot -t culicidaelab-nginx:latest .

echo "Starting containers with SSL..."
DOMAIN=culicidaelab.ru \
EMAIL=admin@culicidaelab.ru \
SSL_ENABLED=true \
CORS_ORIGINS=https://culicidaelab.ru,http://culicidaelab.ru \
CLIENT_BACKEND_URL=https://culicidaelab.ru \
STATIC_FILES_URL=https://culicidaelab.ru \
docker-compose -f docker-compose.prebuilt.yml up -d

echo "Waiting for containers to start..."
sleep 10

echo "Checking container status..."
docker-compose -f docker-compose.prebuilt.yml ps

echo "Following nginx logs..."
docker-compose -f docker-compose.prebuilt.yml logs -f nginx