#!/bin/bash

echo "=== SSL Bad Gateway Debug ==="

echo "1. Container Status:"
docker-compose -f docker-compose.ssl.yml --env-file .env.production ps
echo ""

echo "2. Backend Health Check:"
docker exec culicidaelab_backend_ssl curl -f http://localhost:8000/health 2>/dev/null && echo "✓ Backend healthy" || echo "✗ Backend not healthy"
echo ""

echo "3. Frontend Health Check:"
docker exec culicidaelab_frontend_ssl curl -f http://localhost:8765/ 2>/dev/null && echo "✓ Frontend healthy" || echo "✗ Frontend not healthy"
echo ""

echo "4. Network Connectivity (nginx -> backend):"
docker exec culicidaelab_nginx_ssl curl -f http://backend:8000/health 2>/dev/null && echo "✓ Nginx can reach backend" || echo "✗ Nginx cannot reach backend"
echo ""

echo "5. Network Connectivity (nginx -> frontend):"
docker exec culicidaelab_nginx_ssl curl -f http://frontend:8765/ 2>/dev/null && echo "✓ Nginx can reach frontend" || echo "✗ Nginx cannot reach frontend"
echo ""

echo "6. Backend Logs (last 10 lines):"
docker logs culicidaelab_backend_ssl --tail 10
echo ""

echo "7. Frontend Logs (last 5 lines):"
docker logs culicidaelab_frontend_ssl --tail 5
echo ""

echo "8. Nginx Logs (last 5 lines):"
docker logs culicidaelab_nginx_ssl --tail 5
echo ""

echo "9. Docker Network Info:"
docker network inspect culicidaelab-server_culicidaelab_network | grep -A 5 -B 5 "IPv4Address"
echo ""

echo "=== Debug Complete ==="