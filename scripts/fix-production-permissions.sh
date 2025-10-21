#!/bin/bash

echo "=== Fixing Production Permissions ==="

# Ensure containers are running
echo "1. Starting containers..."
docker-compose -f docker-compose.ssl.yml --env-file .env.production up -d

# Wait for containers to start
echo "2. Waiting for containers to start..."
sleep 10

# Fix permissions in backend container
echo "3. Creating directories and fixing permissions..."
docker exec culicidaelab_backend_ssl bash -c "
    mkdir -p /app/backend/static/images/predicted/original
    mkdir -p /app/backend/static/images/predicted/224x224  
    mkdir -p /app/backend/static/images/predicted/100x100
    chmod -R 755 /app/backend/static/images/predicted
    ls -la /app/backend/static/images/predicted/
"

# Test backend health
echo "4. Testing backend health..."
docker exec culicidaelab_backend_ssl curl -f http://localhost:8000/health || echo "Backend health check failed"

# Test if backend can write to predicted directory
echo "5. Testing write permissions..."
docker exec culicidaelab_backend_ssl touch /app/backend/static/images/predicted/test_write.txt && echo "Write test successful" || echo "Write test failed"

# Check environment variables
echo "6. Checking environment variables..."
docker exec culicidaelab_backend_ssl env | grep CULICIDAELAB

echo "=== Fix Complete ==="