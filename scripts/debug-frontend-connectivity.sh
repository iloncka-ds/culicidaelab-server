#!/bin/bash

echo "=== Frontend Connectivity Debug ==="

echo "1. Frontend container status:"
docker ps | grep frontend || echo "Frontend container not found"
echo ""

echo "2. Frontend container logs (last 20 lines):"
docker logs culicidaelab_frontend_ssl --tail 20
echo ""

echo "3. Test frontend from nginx container:"
docker exec culicidaelab_nginx_ssl curl -v http://frontend:8765/ 2>&1 || echo "Cannot reach frontend from nginx"
echo ""

echo "4. Test frontend from backend container:"
docker exec culicidaelab_backend_ssl curl -v http://frontend:8765/ 2>&1 || echo "Cannot reach frontend from backend"
echo ""

echo "5. Frontend container network info:"
docker exec culicidaelab_frontend_ssl ip addr show eth0 2>/dev/null || echo "Cannot get frontend IP"
echo ""

echo "6. Nginx container network info:"
docker exec culicidaelab_nginx_ssl ip addr show eth0 2>/dev/null || echo "Cannot get nginx IP"
echo ""

echo "7. Test if frontend port is listening:"
docker exec culicidaelab_frontend_ssl netstat -tlnp | grep 8765 || echo "Port 8765 not listening"
echo ""

echo "8. Frontend environment variables:"
docker exec culicidaelab_frontend_ssl env | grep -E "(CLIENT_BACKEND_URL|SERVER_BACKEND_URL|STATIC_FILES_URL)"
echo ""

echo "9. Docker network inspection:"
docker network ls | grep culicidaelab
docker network inspect culicidaelab-server_culicidaelab_network | grep -A 10 -B 5 "frontend\|nginx"
echo ""

echo "=== Debug Complete ==="