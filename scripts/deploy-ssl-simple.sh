#!/bin/bash

echo "=== CulicidaeLab SSL Deployment ==="

# Stop existing containers
echo "1. Stopping existing containers..."
docker-compose -f docker-compose.ssl.yml --env-file .env.production down

# Remove old volumes if needed (uncomment if you want fresh start)
# docker volume rm culicidaelab-server_backend_static 2>/dev/null || true

# Pull latest images
echo "2. Pulling latest images..."
docker-compose -f docker-compose.ssl.yml --env-file .env.production pull

# Start services
echo "3. Starting services..."
docker-compose -f docker-compose.ssl.yml --env-file .env.production up -d

# Wait for services to start
echo "4. Waiting for services to start..."
sleep 15

# Check status
echo "5. Checking container status..."
docker-compose -f docker-compose.ssl.yml --env-file .env.production ps

# Fix permissions
echo "6. Fixing permissions..."
docker exec culicidaelab_backend_ssl bash -c "
    mkdir -p /app/backend/static/images/predicted/{original,224x224,100x100}
    chmod -R 755 /app/backend/static/images/predicted
    echo 'Permissions fixed'
" 2>/dev/null || echo "Could not fix permissions (container might not be ready)"

# Test health
echo "7. Testing health endpoints..."
sleep 5
docker exec culicidaelab_backend_ssl curl -f http://localhost:8000/health 2>/dev/null && echo "✓ Backend healthy" || echo "✗ Backend not healthy"

echo ""
echo "=== Deployment Complete ==="
echo "Check logs with: docker-compose -f docker-compose.ssl.yml --env-file .env.production logs"
echo "Access your site at: https://$(grep DOMAIN .env.production | cut -d= -f2)"