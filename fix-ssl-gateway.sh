#!/bin/bash

echo "=== Fixing SSL Bad Gateway ==="

echo "1. Stopping all containers..."
docker-compose -f docker-compose.ssl.yml --env-file .env.production down

echo "2. Rebuilding backend (to use new entrypoint)..."
docker-compose -f docker-compose.ssl.yml --env-file .env.production build backend

echo "3. Starting containers..."
docker-compose -f docker-compose.ssl.yml --env-file .env.production up -d

echo "4. Waiting for containers to start..."
sleep 15

echo "5. Checking status..."
docker-compose -f docker-compose.ssl.yml --env-file .env.production ps

echo "6. Testing connectivity..."
echo "Backend health:"
docker exec culicidaelab_backend_ssl curl -f http://localhost:8000/health 2>/dev/null && echo "✓ OK" || echo "✗ Failed"

echo "Frontend health:"
docker exec culicidaelab_frontend_ssl curl -f http://localhost:8765/ 2>/dev/null && echo "✓ OK" || echo "✗ Failed"

echo ""
echo "=== Fix Complete ==="
echo "Try accessing: https://$(grep DOMAIN .env.production | cut -d= -f2)"