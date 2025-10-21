#!/bin/bash

echo "=== Restarting SSL Production Services ==="

echo "1. Stopping all services..."
docker-compose -f docker-compose.ssl.yml --env-file .env.production down

echo "2. Rebuilding backend with fixed permissions..."
docker-compose -f docker-compose.ssl.yml --env-file .env.production build backend

echo "3. Starting services in proper order..."
echo "   Starting backend first..."
docker-compose -f docker-compose.ssl.yml --env-file .env.production up -d backend

echo "   Waiting for backend to be ready..."
sleep 10

echo "   Starting frontend..."
docker-compose -f docker-compose.ssl.yml --env-file .env.production up -d frontend

echo "   Waiting for frontend to be ready..."
sleep 10

echo "   Starting nginx-ssl..."
docker-compose -f docker-compose.ssl.yml --env-file .env.production up -d nginx-ssl

echo "4. Checking final status..."
sleep 5
docker-compose -f docker-compose.ssl.yml --env-file .env.production ps

echo ""
echo "=== Restart Complete ==="
echo "Services should now be running properly"
echo "Check https://$(grep DOMAIN .env.production | cut -d= -f2)"