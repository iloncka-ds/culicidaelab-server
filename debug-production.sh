#!/bin/bash

echo "=== Checking Production Deployment Status ==="
echo ""

echo "1. Container Status:"
docker-compose -f docker-compose.ssl.yml --env-file .env.production ps
echo ""

echo "2. Init-static container logs:"
docker logs culicidaelab-server-init-static-1 2>/dev/null || echo "Init-static container not found or no logs"
echo ""

echo "3. Backend container logs (last 20 lines):"
docker logs culicidaelab_backend_ssl --tail 20 2>/dev/null || echo "Backend container not found"
echo ""

echo "4. Frontend container logs (last 10 lines):"
docker logs culicidaelab_frontend_ssl --tail 10 2>/dev/null || echo "Frontend container not found"
echo ""

echo "5. Nginx container logs (last 10 lines):"
docker logs culicidaelab_nginx_ssl --tail 10 2>/dev/null || echo "Nginx container not found"
echo ""

echo "6. Network connectivity test:"
docker exec culicidaelab_backend_ssl curl -f http://localhost:8000/health 2>/dev/null || echo "Backend health check failed"
echo ""

echo "7. Static directory permissions:"
docker exec culicidaelab_backend_ssl ls -la /app/backend/static/images/ 2>/dev/null || echo "Cannot access static directory"
echo ""

echo "8. Volume inspection:"
docker volume ls | grep culicidaelab
echo ""

echo "=== Debug Complete ==="