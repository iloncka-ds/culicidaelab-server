#!/bin/bash

echo "=== SSL Production Debug ==="

echo "1. Container Status:"
docker-compose -f docker-compose.ssl.yml --env-file .env.production ps

echo ""
echo "2. Backend Health Check:"
if docker exec culicidaelab_backend_ssl curl -f http://localhost:8000/health 2>/dev/null; then
    echo "✓ Backend is healthy"
else
    echo "✗ Backend health check failed"
    echo "Backend logs (last 20 lines):"
    docker logs culicidaelab_backend_ssl --tail 20
fi

echo ""
echo "3. Frontend Health Check:"
if docker exec culicidaelab_frontend_ssl curl -f http://localhost:8765/ 2>/dev/null; then
    echo "✓ Frontend is healthy"
else
    echo "✗ Frontend health check failed"
    echo "Frontend logs (last 20 lines):"
    docker logs culicidaelab_frontend_ssl --tail 20
fi

echo ""
echo "4. Nginx Configuration Test:"
if docker exec culicidaelab_nginx_ssl nginx -t 2>/dev/null; then
    echo "✓ Nginx configuration is valid"
else
    echo "✗ Nginx configuration is invalid"
    echo "Nginx logs (last 20 lines):"
    docker logs culicidaelab_nginx_ssl --tail 20
fi

echo ""
echo "5. Network Connectivity Test:"
echo "Backend to Frontend:"
docker exec culicidaelab_backend_ssl curl -f http://frontend:8765/ 2>/dev/null && echo "✓ OK" || echo "✗ Failed"

echo "Nginx to Backend:"
docker exec culicidaelab_nginx_ssl curl -f http://backend:8000/health 2>/dev/null && echo "✓ OK" || echo "✗ Failed"

echo "Nginx to Frontend:"
docker exec culicidaelab_nginx_ssl curl -f http://frontend:8765/ 2>/dev/null && echo "✓ OK" || echo "✗ Failed"

echo ""
echo "6. Volume Permissions:"
echo "Backend static directory:"
docker exec culicidaelab_backend_ssl ls -la /app/backend/static/images/predicted/ 2>/dev/null || echo "Cannot access directory"

echo ""
echo "7. Environment Variables:"
echo "Domain: $(grep DOMAIN .env.production | cut -d= -f2)"
echo "SSL Enabled: $(grep SSL_ENABLED .env.production | cut -d= -f2)"

echo ""
echo "=== Debug Complete ==="