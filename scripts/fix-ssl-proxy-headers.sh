#!/bin/bash

# Script to fix SSL proxy header warnings in Solara frontend
# This script rebuilds the frontend image with proper proxy header configuration

set -e

echo "🔧 Fixing SSL proxy header configuration..."

# Check if .env.production exists
if [ ! -f ".env.production" ]; then
    echo "❌ Error: .env.production file not found"
    echo "Please ensure you have a production environment file configured"
    exit 1
fi

# Stop the current SSL services
echo "🛑 Stopping current SSL services..."
docker-compose -f docker-compose.ssl-simple.yml --env-file .env.production down

# Rebuild the frontend image with proxy header fixes
echo "🔨 Rebuilding frontend image with proxy header configuration..."
docker build -t iloncka/culicidaelab-frontend:0.1.1 -f frontend/Dockerfile frontend/

# Start the services again
echo "🚀 Starting SSL services with fixed configuration..."
docker-compose -f docker-compose.ssl-simple.yml --env-file .env.production up -d

# Show the logs to verify the fix
echo "📋 Showing frontend logs to verify the fix..."
sleep 10
docker logs culicidaelab_frontend_ssl --tail 20

echo "✅ SSL proxy header fix applied!"
echo "The Solara server should now properly handle forwarded headers from nginx."
echo ""
echo "Monitor the logs with:"
echo "docker logs -f culicidaelab_frontend_ssl"