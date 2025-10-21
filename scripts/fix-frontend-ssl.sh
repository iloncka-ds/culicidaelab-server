#!/bin/bash

echo "=== Fixing Frontend SSL Issues ==="

echo "1. Restarting frontend container..."
docker-compose -f docker-compose.ssl.yml --env-file .env.production restart frontend

echo "2. Waiting for frontend to start..."
sleep 10

echo "3. Checking frontend status..."
docker ps | grep frontend

echo "4. Testing frontend health..."
for i in {1..5}; do
    echo "Attempt $i:"
    docker exec culicidaelab_frontend_ssl curl -f http://localhost:8765/ 2>/dev/null && echo "✓ Frontend responding" && break
    echo "✗ Frontend not responding, waiting..."
    sleep 5
done

echo "5. Testing from nginx container..."
docker exec culicidaelab_nginx_ssl curl -f http://frontend:8765/ 2>/dev/null && echo "✓ Nginx can reach frontend" || echo "✗ Nginx cannot reach frontend"

echo "6. Frontend logs (last 10 lines):"
docker logs culicidaelab_frontend_ssl --tail 10

echo ""
echo "=== Fix Complete ==="
echo "Try accessing your site now: https://$(grep DOMAIN .env.production | cut -d= -f2)"