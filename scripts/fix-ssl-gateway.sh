#!/bin/bash

echo "=== Fixing SSL Bad Gateway ==="

echo "1. Stopping all containers..."
docker-compose -f docker-compose.ssl.yml --env-file .env.production down

echo "2. Cleaning up volumes to fix permission issues..."
docker volume rm culicidaelab_backend_static 2>/dev/null || echo "Volume already removed or doesn't exist"

echo "3. Rebuilding backend with fixed permissions..."
docker-compose -f docker-compose.ssl.yml --env-file .env.production build --no-cache backend

echo "4. Starting backend first to ensure it's ready..."
docker-compose -f docker-compose.ssl.yml --env-file .env.production up -d backend

echo "5. Waiting for backend to be healthy..."
echo "Checking backend health..."
for i in {1..30}; do
    if docker exec culicidaelab_backend_ssl curl -f http://localhost:8000/health 2>/dev/null; then
        echo "✓ Backend is healthy after ${i} attempts"
        break
    fi
    echo "Attempt $i/30: Backend not ready yet, waiting..."
    sleep 2
done

echo "6. Starting frontend..."
docker-compose -f docker-compose.ssl.yml --env-file .env.production up -d frontend

echo "7. Waiting for frontend to be ready..."
sleep 10
for i in {1..15}; do
    if docker exec culicidaelab_frontend_ssl curl -f http://localhost:8765/ 2>/dev/null; then
        echo "✓ Frontend is healthy after ${i} attempts"
        break
    fi
    echo "Attempt $i/15: Frontend not ready yet, waiting..."
    sleep 2
done

echo "8. Starting nginx-ssl..."
docker-compose -f docker-compose.ssl.yml --env-file .env.production up -d nginx-ssl

echo "9. Final status check..."
sleep 5
docker-compose -f docker-compose.ssl.yml --env-file .env.production ps

echo "10. Testing all services..."
echo "Backend health:"
docker exec culicidaelab_backend_ssl curl -f http://localhost:8000/health 2>/dev/null && echo "✓ OK" || echo "✗ Failed"

echo "Frontend health:"
docker exec culicidaelab_frontend_ssl curl -f http://localhost:8765/ 2>/dev/null && echo "✓ OK" || echo "✗ Failed"

echo "Nginx config test:"
docker exec culicidaelab_nginx_ssl nginx -t 2>/dev/null && echo "✓ OK" || echo "✗ Failed"

echo ""
echo "=== Fix Complete ==="
echo "Try accessing: https://$(grep DOMAIN .env.production | cut -d= -f2)"
echo ""
echo "If issues persist, check logs with:"
echo "docker-compose -f docker-compose.ssl.yml --env-file .env.production logs backend"
echo "docker-compose -f docker-compose.ssl.yml --env-file .env.production logs nginx-ssl"